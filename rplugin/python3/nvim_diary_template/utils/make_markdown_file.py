"""make_markdown_file

Functions to open the markdown files from the filesystem, or make them if
they don't exist.
"""

from datetime import date

from nvim_diary_template.helpers.issue_helpers import convert_issues
from nvim_diary_template.helpers.neovim_helpers import (is_buffer_empty,
                                                        set_buffer_contents)
from nvim_diary_template.utils.make_issues import produce_issue_markdown
from nvim_diary_template.utils.make_schedule import produce_schedule_markdown


def make_todays_diary(nvim,
                      options,
                      gcal_service,
                      github_service,
                      auto_command=False):
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
            nvim.err_write(
                "Buffer is not empty, can't create diary.\n"
            )
        return

    # If options is none, then everything else proably wasn't setup either.
    if options is None:
        nvim.err_write(
            "Options weren't initialised, aborting.\n"
        )
        return

    full_markdown = []

    diary_metadata = {
        "Date": str(date.today())
    }

    full_markdown.extend(generate_markdown_metadata(diary_metadata))

    for heading in options.daily_headings:
        full_markdown.append(f"# {heading}")
        full_markdown.append("")

    # Add in issues section
    if not github_service or not github_service.active:
        issues = convert_issues(github_service)
    else:
        issues = []

    issue_markdown = produce_issue_markdown(issues)
    full_markdown.extend(issue_markdown)

    # Add in Todays Calendar Entries
    if not gcal_service or not gcal_service.active:
        todays_events = gcal_service.todays_events
    else:
        todays_events = []

    schedule_markdown = produce_schedule_markdown(todays_events)
    full_markdown.extend(schedule_markdown)

    set_buffer_contents(nvim, full_markdown)
    nvim.command(":w")


def generate_markdown_metadata(metadata_obj):
    """generate_markdown_metadata

    Add some basic metadata to the top of the file
    in HTML tags.
    """

    metadata = []

    metadata.append("<!---")

    passed_metadata = [
        f"    {key}: {value}" for key, value in metadata_obj.items()
    ]

    metadata.extend(passed_metadata)
    metadata.append(f"    Tags:")
    metadata.append("--->")
    metadata.append("")

    return metadata
