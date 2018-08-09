"""make_markdown_file

Functions to open the markdown files from the filesystem, or make them if
they don't exist.
"""

from datetime import date
from typing import Dict, List

from neovim import Nvim

from ..classes.calendar_event_class import CalendarEvent
from ..classes.github_issue_class import GitHubIssue
from ..classes.nvim_github_class import SimpleNvimGithub
from ..classes.nvim_google_cal_class import SimpleNvimGoogleCal
from ..classes.plugin_options import PluginOptions
from ..helpers.neovim_helpers import is_buffer_empty, set_buffer_contents
from ..utils.make_issues import produce_issue_markdown
from ..utils.make_schedule import produce_schedule_markdown


def make_todays_diary(
    nvim: Nvim,
    options: PluginOptions,
    gcal_service: SimpleNvimGoogleCal,
    github_service: SimpleNvimGithub,
    auto_command: bool = False,
):
    """make_todays_diary

    Make the actual diary markdown file.
    This includes the following steps:
        * Open the file if it already exists.
        * If not, put the default template in and save.
    """

    # If the buffer is not empty, don't continue. Issue an error if manually
    # called, don't issue an error for an autocommand.
    if not is_buffer_empty(nvim):
        if not auto_command:
            nvim.err_write("Buffer is not empty, can't create diary.\n")
        return

    # If options is none, then everything else proably wasn't setup either.
    if options is None:
        nvim.err_write("Options weren't initialised, aborting.\n")
        return

    full_markdown: List[str] = []

    diary_metadata: Dict[str, str] = {"Date": str(date.today())}

    full_markdown.extend(generate_markdown_metadata(diary_metadata))

    for heading in options.daily_headings:
        full_markdown.append(f"# {heading}")
        full_markdown.append("")

    # Add in issues section
    issues: List[GitHubIssue] = []
    if options.use_github_repo and github_service and github_service.active:
        issues = github_service.issues

    issue_markdown: List[str] = produce_issue_markdown(issues)
    full_markdown.extend(issue_markdown)

    # Add in Todays Calendar Entries
    todays_events: List[CalendarEvent] = []
    if options.use_google_calendar and gcal_service and gcal_service.active:
        todays_events = gcal_service.events

    schedule_markdown: List[str] = produce_schedule_markdown(todays_events)
    full_markdown.extend(schedule_markdown)

    # Set the buffer contents and save the file.
    set_buffer_contents(nvim, full_markdown)
    nvim.command(":w")


def generate_markdown_metadata(metadata_obj: Dict[str, str]) -> List[str]:
    """generate_markdown_metadata

    Add some basic metadata to the top of the file
    in HTML tags.
    """

    metadata: List[str] = ["<!---"]

    passed_metadata: List[str] = [
        f"    {key}: {value}" for key, value in metadata_obj.items()
    ]

    metadata.extend(passed_metadata)
    metadata.append(f"    Tags:")
    metadata.append("--->")
    metadata.append("")

    return metadata
