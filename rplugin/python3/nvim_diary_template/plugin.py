# pylint: disable=missing-docstring, keyword-arg-before-vararg, W0201
from datetime import date
from typing import Any, List

import pynvim
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
from .utils.constants import ISO_FORMAT
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


@pynvim.plugin
class DiaryTemplatePlugin:
    def __init__(self, nvim: pynvim.Nvim) -> None:
        self._nvim: pynvim.Nvim = nvim
        self._fully_setup: bool = False

    @pynvim.function("DiaryOptionsInit", sync=False)
    def check_options(self, *_: List[str]) -> None:
        if not self._fully_setup:
            self.options: PluginOptions = PluginOptions(self._nvim)
            self._gcal_service: SimpleNvimGoogleCal = SimpleNvimGoogleCal(
                self._nvim, self.options
            )
            self._github_service: SimpleNvimGithub = SimpleNvimGithub(
                self._nvim, self.options
            )
            self._fully_setup = True

    @pynvim.function("DiaryInit", sync=True)
    def init_diary(self, *_: List[str]) -> None:
        self.check_options()
        self.make_diary_command(called_from_autocommand=True)

    @pynvim.function("DiaryMake", sync=True)
    def make_diary_command(
        self, called_from_autocommand: bool = False, *_: List[str]
    ) -> None:
        self.check_options()
        make_diary(
            self._nvim,
            self.options,
            self._gcal_service,
            self._github_service,
            auto_command=called_from_autocommand,
        )

    @pynvim.function("DiaryUploadCalendar", sync=True)
    def upload_to_calendar(self, *_: List[str]) -> None:
        markdown_events: List[CalendarEvent] = parse_markdown_file_for_events(
            self._nvim, ISO_FORMAT
        )

        buffer_date: date = parser.parse(get_diary_date(self._nvim)).date()
        self._gcal_service.upload_to_calendar(markdown_events, buffer_date)

        remove_events_not_from_today(self._nvim)
        format_markdown_events(self._nvim)

    @pynvim.function("DiaryGetCalendar", sync=True)
    def grab_from_calendar(self, *_: List[str]) -> None:
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

    @pynvim.function("DiaryUpdateCalendar", sync=True)
    def update_calendar(self, *_: List[str]) -> None:
        self.upload_to_calendar()
        self.grab_from_calendar()

    @pynvim.function("DiarySortCalendar", sync=True)
    def sort_calendar(self, *_: List[str]) -> None:
        sort_markdown_events(self._nvim)

    @pynvim.function("DiaryGetIssues", sync=True)
    def get_issues(self, *_: List[str]) -> None:
        markdown_issues: List[GitHubIssue] = parse_markdown_file_for_issues(self._nvim)
        github_issues: List[GitHubIssue] = self._github_service.get_all_open_issues()

        combined_issues: List[GitHubIssue] = combine_issues(
            self._nvim, markdown_issues, github_issues
        )

        set_issues_from_issues_list(self._nvim, self.options, combined_issues, True)

    @pynvim.function("DiarySortIssues", sync=True)
    def sort_issues(self, *_: List[str]) -> None:
        markdown_issues: List[GitHubIssue] = parse_markdown_file_for_issues(self._nvim)
        set_issues_from_issues_list(self._nvim, self.options, markdown_issues, True)

    @pynvim.function("DiaryInsertIssue", sync=True)
    def insert_issue(self, *_: List[str]) -> None:
        insert_new_issue(self._nvim, self.options)

    @pynvim.function("DiaryInsertComment", sync=True)
    def insert_comment(self, *_: List[str]) -> None:
        insert_new_comment(self._nvim)

    @pynvim.function("DiaryEditComment", sync=True)
    def edit_comment(self, *_: List[str]) -> None:
        insert_edit_tag(self._nvim, "comment")

    @pynvim.function("DiaryEditIssue", sync=True)
    def edit_issue(self, *_: List[str]) -> None:
        insert_edit_tag(self._nvim, "issue")

    @pynvim.function("DiaryUploadNew", sync=True)
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

    @pynvim.function("DiaryUploadEdits", sync=True)
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

    @pynvim.function("DiaryCompleteIssue", sync=True)
    def toggle_completion(self, *_: List[str]) -> None:
        toggle_issue_completion(self._nvim)

    @pynvim.function("DiaryUploadCompletion", sync=True)
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

    @pynvim.function("DiaryUploadIssues", sync=True)
    def upload_all_issues(self, *_: List[str]) -> None:
        self.upload_new_issues(True)
        self.upload_edited_issues(True)
        self.upload_issue_completions(True)

        self.flush_messages()

    @pynvim.function("DiarySwapGroupSorting", sync=True)
    def swap_group_sorting(self, *_: List[str]) -> None:
        def rotate(input_list: List[Any], pivot: int) -> List[Any]:
            return input_list[pivot:] + input_list[:pivot]

        self.options.issue_groups = rotate(self.options.issue_groups, 1)
        self.sort_issues()

    def flush_messages(self, *_: List[str]) -> None:
        self._nvim.out_write("\n")
