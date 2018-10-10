# pylint: disable=missing-docstring
from functools import wraps
from typing import Any, Callable, List

import neovim
from dateutil import parser

from .classes.calendar_event_class import CalendarEvent
from .classes.github_issue_class import GitHubIssue
from .classes.nvim_github_class import SimpleNvimGithub
from .classes.nvim_google_cal_class import SimpleNvimGoogleCal
from .classes.plugin_options import PluginOptions
from .helpers.issue_helpers import (
    insert_edit_tag,
    insert_new_comment,
    insert_new_issue,
    toggle_issue_completion,
)
from .helpers.markdown_helpers import sort_markdown_events
from .helpers.neovim_helpers import get_diary_date
from .utils.constants import FILE_TYPE_WILDCARD, ISO_FORMAT
from .utils.make_issues import remove_tag_from_issues, set_issues_from_issues_list
from .utils.make_markdown_file import make_diary
from .utils.make_schedule import set_schedule_from_events_list
from .utils.parse_markdown import (
    combine_events,
    combine_issues,
    parse_markdown_file_for_events,
    parse_markdown_file_for_issues,
    remove_events_not_from_today,
)


@neovim.plugin
class DiaryTemplatePlugin:
    def __init__(self, nvim: neovim.Nvim) -> None:
        self._nvim: neovim.Nvim = nvim
        self._gcal_service: Any = None
        self._github_service: Any = None
        self.options: Any = None

    def check_options(self) -> None:
        if self.options is None:
            self.options = PluginOptions(self._nvim)
            self._gcal_service = SimpleNvimGoogleCal(self._nvim, self.options)
            self._github_service = SimpleNvimGithub(self._nvim, self.options)

    @neovim.autocmd("BufEnter", pattern=FILE_TYPE_WILDCARD, sync=True)
    def event_buf_enter(self) -> None:
        self.check_options()
        self.make_diary(called_from_autocommand=True)

    @neovim.command("DiaryMake")
    def make_diary(self, called_from_autocommand: bool = False) -> None:
        make_diary(
            self._nvim,
            self.options,
            self._gcal_service,
            self._github_service,
            auto_command=called_from_autocommand,
        )

    @neovim.command("DiaryUploadCalendar")
    def upload_to_calendar(self) -> None:
        markdown_events: List[CalendarEvent] = parse_markdown_file_for_events(
            self._nvim, ISO_FORMAT
        )

        buffer_date: str = get_diary_date(self._nvim)
        self._gcal_service.upload_to_calendar(markdown_events, buffer_date)
        remove_events_not_from_today(self._nvim)

    @neovim.command("DiaryGetCalendar")
    def grab_from_calendar(self) -> None:
        buffer_date: str = get_diary_date(self._nvim)

        markdown_events: List[CalendarEvent] = parse_markdown_file_for_events(
            self._nvim, ISO_FORMAT
        )
        cal_events: List[CalendarEvent] = self._gcal_service.get_events_for_date(
            parser.parse(buffer_date)
        )

        combined_events: List[CalendarEvent] = combine_events(
            markdown_events, cal_events
        )
        set_schedule_from_events_list(self._nvim, combined_events, False)
        self.sort_calendar()

    @neovim.command("DiaryUpdateCalendar")
    def update_calendar(self) -> None:
        self.upload_to_calendar()
        self.grab_from_calendar()

    @neovim.command("DiarySortCalendar")
    def sort_calendar(self) -> None:
        sort_markdown_events(self._nvim)

    @neovim.command("DiaryGetIssues")
    def get_issues(self) -> None:
        markdown_issues: List[GitHubIssue] = parse_markdown_file_for_issues(self._nvim)
        github_issues: List[GitHubIssue] = self._github_service.get_all_open_issues()

        combined_issues: List[GitHubIssue] = combine_issues(
            self._nvim, markdown_issues, github_issues
        )

        set_issues_from_issues_list(self._nvim, combined_issues, True)

    @neovim.command("DiarySortIssues")
    def sort_issues(self) -> None:
        markdown_issues: List[GitHubIssue] = parse_markdown_file_for_issues(self._nvim)
        set_issues_from_issues_list(self._nvim, markdown_issues, True)

    @neovim.command("DiaryInsertIssue")
    def insert_issue(self) -> None:
        insert_new_issue(self._nvim)

    @neovim.command("DiaryInsertComment")
    def insert_comment(self) -> None:
        insert_new_comment(self._nvim)

    @neovim.command("DiaryEditComment")
    def edit_comment(self) -> None:
        insert_edit_tag(self._nvim, "comment")

    @neovim.command("DiaryEditIssue")
    def edit_issue(self) -> None:
        insert_edit_tag(self._nvim, "issue")

    @neovim.command("DiaryUploadNew")
    def upload_new_issues(self, buffered: bool = False) -> None:
        issues: List[GitHubIssue] = parse_markdown_file_for_issues(self._nvim)

        issues, ignore_list = self._github_service.upload_issues(issues, "new")
        issues = remove_tag_from_issues(issues, "new", "issues", ignore_list)

        issues, ignore_list = self._github_service.upload_comments(issues, "new")
        issues_without_new_tag: List[GitHubIssue] = remove_tag_from_issues(
            issues, "new", "comments", ignore_list
        )

        set_issues_from_issues_list(
            self._nvim, issues_without_new_tag, self.options.sort_issues_on_upload
        )

        if not buffered:
            self.flush_messages()

    @neovim.command("DiaryUploadEdits")
    def upload_edited_issues(self, buffered: bool = False) -> None:
        issues: List[GitHubIssue] = parse_markdown_file_for_issues(self._nvim)

        issues, ignore_list = self._github_service.update_comments(issues, "edit")
        issues = remove_tag_from_issues(issues, "edit", "comments", ignore_list)

        issues, ignore_list = self._github_service.update_issues(issues, "edit")
        issues_without_edit_tag: List[GitHubIssue] = remove_tag_from_issues(
            issues, "edit", "issues", ignore_list
        )

        set_issues_from_issues_list(
            self._nvim, issues_without_edit_tag, self.options.sort_issues_on_upload
        )

        if not buffered:
            self.flush_messages()

    @neovim.command("DiaryCompleteIssue")
    def toggle_completion(self) -> None:
        toggle_issue_completion(self._nvim)

    @neovim.command("DiaryUploadCompletion")
    def upload_issue_completions(self, buffered: bool = False) -> None:
        issues: List[GitHubIssue] = parse_markdown_file_for_issues(self._nvim)
        self._github_service.complete_issues(issues)

        # Despite no changes happening here, we want to set the issues again to
        # sort them.
        set_issues_from_issues_list(
            self._nvim, issues, self.options.sort_issues_on_upload
        )

        if not buffered:
            self.flush_messages()

    @neovim.command("DiaryUploadIssues")
    def upload_all_issues(self) -> None:
        self.upload_new_issues(True)
        self.upload_edited_issues(True)
        self.upload_issue_completions(True)

        self.flush_messages()

    def flush_messages(self) -> None:
        self._nvim.out_write("\n")


def if_active(function: Callable) -> Callable:
    """if_active

    A decorator for a function, such that it is only run when
    nvim_diary_template is ready.

    Taken from numirias/semshi
    """

    @wraps(function)
    def wrapper(self: DiaryTemplatePlugin) -> None:
        if not self.options.active:
            return
        function(self)

    return wrapper
