# pylint: disable=missing-docstring
from functools import wraps

import neovim

from nvim_diary_template.helpers.issue_helpers import (insert_edit_tag,
                                                       insert_new_comment,
                                                       insert_new_issue)
from nvim_diary_template.helpers.markdown_helpers import sort_markdown_events
from nvim_diary_template.utils.constants import FILE_TYPE_WILDCARD, ISO_FORMAT
from nvim_diary_template.utils.make_issues import (remove_tag_from_comments,
                                                   set_issues_from_issues_list)
from nvim_diary_template.utils.make_markdown_file import make_todays_diary
from nvim_diary_template.utils.make_schedule import \
    set_schedule_from_events_list
from nvim_diary_template.utils.nvim_github_class import SimpleNvimGithub
from nvim_diary_template.utils.nvim_google_cal_class import SimpleNvimGoogleCal
from nvim_diary_template.utils.parse_markdown import (combine_events,
                                                      parse_markdown_file_for_events,
                                                      parse_markdown_file_for_issues,
                                                      remove_events_not_from_today)
from nvim_diary_template.utils.plugin_options import PluginOptions


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
class DiaryTemplatePlugin(object):

    def __init__(self, nvim):
        self._nvim = nvim
        self._options = None
        self._gcal_service = None
        self._github_service = None

    @neovim.autocmd('BufEnter', pattern=FILE_TYPE_WILDCARD, sync=True)
    def event_buf_enter(self):
        if self._options is None:
            self._options = PluginOptions(self._nvim)
            self._gcal_service = SimpleNvimGoogleCal(
                self._nvim,
                self._options
            )
            self._github_service = SimpleNvimGithub(self._nvim, self._options)

    @neovim.command('DiaryMake')
    # @if_active
    def make_diary(self):

        # TODO: Remove this, since it shouldn't be needed due to the autocmds.
        if self._options is None:
            self._options = PluginOptions(self._nvim)
            self._gcal_service = SimpleNvimGoogleCal(
                self._nvim,
                self._options
            )
            self._github_service = SimpleNvimGithub(self._nvim, self._options)

        make_todays_diary(
            self._nvim,
            self._options,
            self._gcal_service,
            self._github_service
        )

    @neovim.command('DiaryUploadCalendar')
    def upload_to_calendar(self):
        markdown_events = parse_markdown_file_for_events(
            self._nvim,
            ISO_FORMAT
        )

        self._gcal_service.upload_to_calendar(markdown_events)
        remove_events_not_from_today(self._nvim)

    @neovim.command('DiaryGrabCalendar')
    def grab_from_calendar(self):
        markdown_events = parse_markdown_file_for_events(
            self._nvim,
            ISO_FORMAT
        )
        cal_events = self._gcal_service.get_events_for_today()

        combined_events = combine_events(
            markdown_events,
            cal_events
        )
        set_schedule_from_events_list(self._nvim, combined_events, False)
        self.sort_calendar()

    @neovim.command('DiaryUpdateCalendar')
    def update_calendar(self):
        self.upload_to_calendar()
        self.grab_from_calendar()

    @neovim.command('DiarySortCalendar')
    def sort_calendar(self):
        sort_markdown_events(self._nvim)

    @neovim.command('DiaryIssue')
    def insert_issue(self):
        insert_new_issue(self._nvim)

    @neovim.command('DiaryIssueComment')
    def insert_comment(self):
        insert_new_comment(self._nvim)

    @neovim.command('DiaryIssueEdit')
    def edit_comment(self):
        insert_edit_tag(self._nvim)

    @neovim.command('DiaryUploadNewComments')
    def upload_new_comments(self):
        issues = parse_markdown_file_for_issues(self._nvim)
        self._github_service.upload_comments(issues, 'new')
        issues_without_new_tag = remove_tag_from_comments(issues, 'new')
        set_issues_from_issues_list(self._nvim, issues_without_new_tag)

    @neovim.command('DiaryUploadCommentEdits')
    def upload_edited_comments(self):
        issues = parse_markdown_file_for_issues(self._nvim)
        self._github_service.update_comments(issues, 'edit')

        issues_without_edit_tag = remove_tag_from_comments(issues, 'edit')
        set_issues_from_issues_list(self._nvim, issues_without_edit_tag)
