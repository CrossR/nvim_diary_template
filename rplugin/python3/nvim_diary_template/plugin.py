# pylint: disable=missing-docstring, W0201
from datetime import date
from typing import Any, List

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
from .helpers.markdown_helpers import format_markdown_events, sort_markdown_events
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
        self._fully_setup: bool = False

    @neovim.function("DiaryOptionsInit", sync=False)
    def check_options(self) -> None:
        if not self._fully_setup:
            self.options: PluginOptions = PluginOptions(self._nvim)
            self._gcal_service: SimpleNvimGoogleCal = SimpleNvimGoogleCal(
                self._nvim, self.options
            )
            self._github_service: SimpleNvimGithub = SimpleNvimGithub(
                self._nvim, self.options
            )
            self._fully_setup = True

    @neovim.function("DiaryInit", sync=True)
    def init_diary(self) -> None:
        self.check_options()
        self.make_diary_command(called_from_autocommand=True)

    @neovim.function("DiaryMake", sync=True)
    def make_diary_command(self, called_from_autocommand: bool = False) -> None:
        self.check_options()
        make_diary(
            self._nvim,
            self.options,
            self._gcal_service,
            self._github_service,
            auto_command=called_from_autocommand,
        )

    @neovim.function("DiaryUploadCalendar", sync=True)
    def upload_to_calendar(self) -> None:
        markdown_events: List[CalendarEvent] = parse_markdown_file_for_events(
            self._nvim, ISO_FORMAT
        )

        buffer_date: date = parser.parse(get_diary_date(self._nvim)).date()
        self._gcal_service.upload_to_calendar(markdown_events, buffer_date)

        remove_events_not_from_today(self._nvim)
        format_markdown_events(self._nvim)

    @neovim.function("DiaryGetCalendar", sync=True)
    def grab_from_calendar(self) -> None:
        buffer_date: date = parser.parse(get_diary_date(self._nvim)).date()

        markdown_events: List[CalendarEvent] = parse_markdown_file_for_events(
            self._nvim, ISO_FORMAT
        )
        cal_events: List[CalendarEvent] = self._gcal_service.get_events_for_date(
            buffer_date
        )

        combined_events: List[CalendarEvent] = combine_events(
            markdown_events, cal_events
        )
        set_schedule_from_events_list(self._nvim, combined_events, False)
        self.sort_calendar()

    @neovim.function("DiaryUpdateCalendar", sync=True)
    def update_calendar(self) -> None:
        self.upload_to_calendar()
        self.grab_from_calendar()

    @neovim.function("DiarySortCalendar", sync=True)
    def sort_calendar(self) -> None:
        sort_markdown_events(self._nvim)

    @neovim.function("DiaryGetIssues", sync=True)
    def get_issues(self) -> None:
        markdown_issues: List[GitHubIssue] = parse_markdown_file_for_issues(self._nvim)
        github_issues: List[GitHubIssue] = self._github_service.get_all_open_issues()

        combined_issues: List[GitHubIssue] = combine_issues(
            self._nvim, markdown_issues, github_issues
        )

        set_issues_from_issues_list(self._nvim, self.options, combined_issues, True)

    @neovim.function("DiarySortIssues", sync=True)
    def sort_issues(self) -> None:
        markdown_issues: List[GitHubIssue] = parse_markdown_file_for_issues(self._nvim)
        set_issues_from_issues_list(self._nvim, self.options, markdown_issues, True)

    @neovim.function("DiaryInsertIssue", sync=True)
    def insert_issue(self) -> None:
        insert_new_issue(self._nvim)

    @neovim.function("DiaryInsertComment", sync=True)
    def insert_comment(self) -> None:
        insert_new_comment(self._nvim)

    @neovim.function("DiaryEditComment", sync=True)
    def edit_comment(self) -> None:
        insert_edit_tag(self._nvim, "comment")

    @neovim.function("DiaryEditIssue", sync=True)
    def edit_issue(self) -> None:
        insert_edit_tag(self._nvim, "issue")

    @neovim.function("DiaryUploadNew", sync=True)
    def upload_new_issues(self, buffered: bool = False) -> None:
        issues: List[GitHubIssue] = parse_markdown_file_for_issues(self._nvim)

        issues, ignore_list = self._github_service.upload_issues(issues, "new")
        issues = remove_tag_from_issues(issues, "new", "issues", ignore_list)

        issues, comment_ignore_list = self._github_service.upload_comments(
            issues, "new"
        )
        issues_without_new_tag: List[GitHubIssue] = remove_tag_from_issues(
            issues, "new", "comments", comment_ignore_list
        )

        set_issues_from_issues_list(
            self._nvim,
            self.options,
            issues_without_new_tag,
            self.options.sort_issues_on_upload,
        )

        if not buffered:
            self.flush_messages()

    @neovim.function("DiaryUploadEdits", sync=True)
    def upload_edited_issues(self, buffered: bool = False) -> None:
        issues: List[GitHubIssue] = parse_markdown_file_for_issues(self._nvim)

        issues, ignore_list = self._github_service.update_comments(issues, "edit")
        issues = remove_tag_from_issues(issues, "edit", "comments", ignore_list)

        issues, issue_ignore_list = self._github_service.update_issues(issues, "edit")
        issues_without_edit_tag: List[GitHubIssue] = remove_tag_from_issues(
            issues, "edit", "issues", issue_ignore_list
        )

        set_issues_from_issues_list(
            self._nvim,
            self.options,
            issues_without_edit_tag,
            self.options.sort_issues_on_upload,
        )

        if not buffered:
            self.flush_messages()

    @neovim.function("DiaryCompleteIssue", sync=True)
    def toggle_completion(self) -> None:
        toggle_issue_completion(self._nvim)

    @neovim.function("DiaryUploadCompletion", sync=True)
    def upload_issue_completions(self, buffered: bool = False) -> None:
        issues: List[GitHubIssue] = parse_markdown_file_for_issues(self._nvim)
        self._github_service.complete_issues(issues)

        # Despite no changes happening here, we want to set the issues again to
        # sort them.
        set_issues_from_issues_list(
            self._nvim, self.options, issues, self.options.sort_issues_on_upload
        )

        if not buffered:
            self.flush_messages()

    @neovim.function("DiaryUploadIssues", sync=True)
    def upload_all_issues(self) -> None:
        self.upload_new_issues(True)
        self.upload_edited_issues(True)
        self.upload_issue_completions(True)

        self.flush_messages()

    @neovim.function("DiarySwapGroupSorting", sync=True)
    def swap_group_sorting(self) -> None:
        def rotate(input_list: List[Any], pivot: int) -> List[Any]:
            return input_list[pivot:] + input_list[:pivot]

        self.options.issue_groups = rotate(self.options.issue_groups, 1)
        self.sort_issues()

    def flush_messages(self) -> None:
        self._nvim.out_write("\n")
