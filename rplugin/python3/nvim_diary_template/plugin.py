# pylint: disable=missing-docstring
from functools import wraps

import neovim

from nvim_diary_template.classes.nvim_github_class import SimpleNvimGithub
from nvim_diary_template.classes.nvim_google_cal_class import SimpleNvimGoogleCal
from nvim_diary_template.classes.plugin_options import PluginOptions
from nvim_diary_template.helpers.issue_helpers import (
    insert_edit_tag,
    insert_new_comment,
    insert_new_issue,
)
from nvim_diary_template.helpers.markdown_helpers import sort_markdown_events
from nvim_diary_template.utils.constants import FILE_TYPE_WILDCARD, ISO_FORMAT
from nvim_diary_template.utils.make_issues import (
    remove_tag_from_issues,
    set_issues_from_issues_list,
)
from nvim_diary_template.utils.make_markdown_file import make_todays_diary
from nvim_diary_template.utils.make_schedule import set_schedule_from_events_list
from nvim_diary_template.utils.parse_markdown import (
    combine_events,
    parse_markdown_file_for_events,
    parse_markdown_file_for_issues,
    remove_events_not_from_today,
)


def if_active(function):
    """if_active

    A decorator for a function, such that it is only run when
    nvim_diary_template is ready.

    Taken from numirias/semshi
    """

    @wraps(function)
    def wrapper(self):
        if not self.options.active:
            return
        function(self)

    return wrapper


@neovim.plugin
class DiaryTemplatePlugin:
    def __init__(self, nvim):
        self._nvim = nvim
        self._options = None
        self._gcal_service = None
        self._github_service = None

    @neovim.autocmd("BufEnter", pattern=FILE_TYPE_WILDCARD, sync=True)
    def event_buf_enter(self):
        if self._options is None:
            self._options = PluginOptions(self._nvim)
            self._gcal_service = SimpleNvimGoogleCal(self._nvim, self._options)
            self._github_service = SimpleNvimGithub(self._nvim, self._options)
        self.make_diary(called_from_autocommand=True)

    @neovim.command("DiaryMake")
    # @if_active
    def make_diary(self, called_from_autocommand=False):
        make_todays_diary(
            self._nvim,
            self._options,
            self._gcal_service,
            self._github_service,
            auto_command=called_from_autocommand,
        )

    @neovim.command("DiaryUploadCalendar")
    def upload_to_calendar(self):
        markdown_events = parse_markdown_file_for_events(self._nvim, ISO_FORMAT)

        self._gcal_service.upload_to_calendar(markdown_events)
        remove_events_not_from_today(self._nvim)

    @neovim.command("DiaryGrabCalendar")
    def grab_from_calendar(self):
        markdown_events = parse_markdown_file_for_events(self._nvim, ISO_FORMAT)
        cal_events = self._gcal_service.get_events_for_today()

        combined_events = combine_events(markdown_events, cal_events)
        set_schedule_from_events_list(self._nvim, combined_events, False)
        self.sort_calendar()

    @neovim.command("DiaryUpdateCalendar")
    def update_calendar(self):
        self.upload_to_calendar()
        self.grab_from_calendar()

    @neovim.command("DiarySortCalendar")
    def sort_calendar(self):
        sort_markdown_events(self._nvim)

    @neovim.command("DiaryInsertIssue")
    def insert_issue(self):
        insert_new_issue(self._nvim)

    @neovim.command("DiaryInsertComment")
    def insert_comment(self):
        insert_new_comment(self._nvim)

    @neovim.command("DiaryEditComment")
    def edit_comment(self):
        insert_edit_tag(self._nvim, "comment")

    @neovim.command("DiaryEditIssue")
    def edit_issue(self):
        insert_edit_tag(self._nvim, "issue")

    @neovim.command("DiaryUploadNew")
    def upload_new_issues(self, buffered=False):
        issues = parse_markdown_file_for_issues(self._nvim)

        issues = self._github_service.upload_issues(issues, "new")
        issues = remove_tag_from_issues(issues, "new", "issues")
        issues = self._github_service.upload_comments(issues, "new")

        issues_without_new_tag = remove_tag_from_issues(issues, "new")
        set_issues_from_issues_list(self._nvim, issues_without_new_tag)

        if not buffered:
            self.flush_messages()

    @neovim.command("DiaryUploadEdits")
    def upload_edited_issues(self, buffered=False):
        issues = parse_markdown_file_for_issues(self._nvim)
        issues = self._github_service.update_comments(issues, "edit")
        issues = self._github_service.update_issues(issues, "edit")

        issues_without_edit_tag = remove_tag_from_issues(issues, "edit")
        set_issues_from_issues_list(self._nvim, issues_without_edit_tag)

        if not buffered:
            self.flush_messages()

    @neovim.command("DiaryUploadCompletion")
    def upload_issue_completions(self, buffered=False):
        issues = parse_markdown_file_for_issues(self._nvim)
        self._github_service.complete_issues(issues)

        # Despite no changes happening here, we want to set the issues again to
        # sort them.
        set_issues_from_issues_list(self._nvim, issues)

        if not buffered:
            self.flush_messages()

    @neovim.command("DiaryUploadIssues")
    def upload_all_issues(self):
        self.upload_new_issues(True)
        self.upload_edited_issues(True)
        self.upload_issue_completions(True)

        self.flush_messages()

    def flush_messages(self):
        self._nvim.out_write("\n")
