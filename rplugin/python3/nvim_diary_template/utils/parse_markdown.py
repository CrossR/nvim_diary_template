"""parse_markdown

Functions for the parsing of the document markdown.
"""

import re
from datetime import date
from typing import List, Match, Optional

from dateutil import parser
from neovim import Nvim

from ..classes.calendar_event_class import CalendarEvent
from ..classes.github_issue_class import GitHubIssue, GitHubIssueComment
from ..helpers.event_helpers import format_event
from ..helpers.google_calendar_helpers import convert_events
from ..helpers.issue_helpers import get_issue_index
from ..helpers.neovim_helpers import (
    get_buffer_contents,
    get_diary_date,
    get_section_line,
    set_line_content,
)
from ..utils.constants import (
    DATETIME_REGEX,
    EVENT_REGEX,
    ISO_FORMAT,
    ISSUE_COMMENT,
    ISSUE_HEADING,
    ISSUE_LABELS,
    ISSUE_METADATA,
    ISSUE_START,
    ISSUE_TITLE,
    SCHEDULE_HEADING,
    TIME_FORMAT,
    TIME_REGEX,
    TODO_IS_CHECKED,
)


def parse_buffer_events(
    event_lines: List[str], format_string: str, diary_date: str
) -> List[CalendarEvent]:
    """parse_buffer_events

    Given a list of event buffer lines, create event objects from them.
    """

    formatted_events: List[CalendarEvent] = []

    for event in event_lines:
        if event == "":
            continue

        # Get the start and end dates.
        # Regex is used to pull out the two substrings.
        matches_date_time: List[str] = re.findall(DATETIME_REGEX, event)

        if not matches_date_time:
            matches_time: List[str] = re.findall(TIME_REGEX, event)
            start_date: str = parser.parse(f"{diary_date} {matches_time[0]}").strftime(
                format_string
            )
            end_date: str = parser.parse(f"{diary_date} {matches_time[1]}").strftime(
                format_string
            )
        else:
            start_date = parser.parse(matches_date_time[0]).strftime(format_string)
            end_date = parser.parse(matches_date_time[1]).strftime(format_string)

        event_name_search: Optional[Match[str]] = re.search(EVENT_REGEX, event)
        event_details: str = event_name_search[
            0
        ] if event_name_search is not None else ""

        formatted_events.append(
            CalendarEvent(name=event_details, start=start_date, end=end_date)
        )

    return formatted_events


def parse_buffer_issues(issue_lines: List[str]) -> List[GitHubIssue]:
    """parse_buffer_issues

    Given a list of issue markdown lines, parse the issue lines and create
    issue objects.
    """

    formatted_issues: List[GitHubIssue] = []
    issue_number: int = -1
    comment_number: int = -1

    for line in issue_lines:
        # If its the start of a new issue, add a new object.
        # Reset the comment number.
        if re.findall(ISSUE_START, line):
            issue_number += 1
            comment_number = -1
            metadata: List[str] = re.findall(ISSUE_METADATA, line)
            labels: List[str] = re.findall(ISSUE_LABELS, line)

            # Strip the leading '+' from the metadata.
            metadata = [tag[1:] for tag in metadata if not tag.startswith("+label")]

            # Strip the leading '+label:' from the labels.
            labels = [label[7:] for label in labels]

            formatted_issues.append(
                GitHubIssue(
                    number=int(re.findall(r"\d+", line)[0]),
                    complete=re.search(TODO_IS_CHECKED, line) is not None,
                    title="",
                    labels=labels,
                    all_comments=[],
                    metadata=metadata,
                )
            )

            continue

        # If its the issue title, then add that to the empty object.
        if re.findall(ISSUE_TITLE, line):
            issue_title: str = re.sub(ISSUE_TITLE, "", line).strip()

            formatted_issues[issue_number].title = issue_title

            continue

        # If this is a comment, start to add it to the existing object.
        if re.findall(ISSUE_COMMENT, line):
            comment_number = int(re.findall(r"\d+", line)[0])
            update_search: Optional[Match[str]] = re.match(ISSUE_COMMENT, line)
            updated_at: str = update_search.group(
                1
            ) if update_search is not None else ""
            comment_metadata: List[str] = re.findall(ISSUE_METADATA, line)

            # Strip the leading '+' from the tags.
            comment_metadata = [tag[1:] for tag in comment_metadata]

            formatted_issues[issue_number].all_comments.append(
                GitHubIssueComment(
                    number=comment_number,
                    tags=comment_metadata,
                    updated_at=updated_at,
                    body=[],
                )
            )

            continue

        # Finally, if there is an issue and comment ongoing, we can add to the
        # current comment.
        if issue_number != -1 and comment_number != -1:
            current_issue: List[GitHubIssueComment] = formatted_issues[
                issue_number
            ].all_comments
            current_comment: List[str] = current_issue[comment_number].body
            current_comment.append(line)

    # Strip any trailing new lines from the comments
    for issue in formatted_issues:
        for comment in issue.all_comments:

            # If the comment has no body, add a single line, to give space to
            # type.
            if comment.body == []:
                comment.body = [""]
                continue

            if comment.body[-1] == "":
                comment.body = comment.body[:-1]

    return formatted_issues


def remove_events_not_from_today(nvim: Nvim) -> None:
    """remove_events_not_from_today

    Remove events from the file if they are not for the correct date.
    """

    current_events: List[CalendarEvent] = parse_markdown_file_for_events(
        nvim, ISO_FORMAT
    )
    date_today: date = parser.parse(get_diary_date(nvim)).date()
    schedule_index: int = get_section_line(
        get_buffer_contents(nvim), SCHEDULE_HEADING
    ) + 1

    for index, event in enumerate(current_events):
        event_date: date = parser.parse(event.start).date()

        if date_today == event_date:
            continue

        event_index: int = schedule_index + index + 1

        set_line_content(nvim, [], event_index, line_offset=1)


def parse_markdown_file_for_events(
    nvim: Nvim, format_string: str
) -> List[CalendarEvent]:
    """parse_markdown_file_for_events

    Gets the contents of the current NeoVim buffer,
    and parses the schedule section into events.
    """

    current_buffer: List[str] = get_buffer_contents(nvim)

    buffer_events_index: int = get_section_line(current_buffer, SCHEDULE_HEADING)
    events: List[str] = current_buffer[buffer_events_index:]
    diary_date: str = get_diary_date(nvim)
    formatted_events: List[CalendarEvent] = parse_buffer_events(
        events, format_string, diary_date
    )

    return formatted_events


def parse_markdown_file_for_issues(nvim: Nvim) -> List[GitHubIssue]:
    """parse_markdown_file_for_issues

    Gets the contents of the current NeoVim buffer,
    and parses the issues section into issues.
    """

    current_buffer: List[str] = get_buffer_contents(nvim)

    # Get the start of each section, to grab the lines between. We plus one to
    # the issues header, to skip the empty line there. We remove two from the
    # events header to remove both the Events header itself, as well as the
    # empty line at the end of the issues section.
    buffer_issues_index: int = get_section_line(current_buffer, ISSUE_HEADING) + 1
    buffer_events_index: int = get_section_line(current_buffer, SCHEDULE_HEADING) - 2

    issue_lines: List[str] = current_buffer[buffer_issues_index:buffer_events_index]
    formatted_issues: List[GitHubIssue] = parse_buffer_issues(issue_lines)

    return formatted_issues


def combine_events(
    markdown_events: List[CalendarEvent], google_events: List[CalendarEvent]
) -> List[CalendarEvent]:
    """combine_events

    Takes both markdown and google events and combines them into a single list,
    with no duplicates.

    The markdown is taken to be the ground truth, as there is no online copy.
    Does not sort events.
    """

    buffer_events: List[CalendarEvent] = [
        format_event(event, ISO_FORMAT) for event in markdown_events
    ]

    formatted_calendar: List[CalendarEvent] = convert_events(google_events, ISO_FORMAT)
    calendar_events: List[CalendarEvent] = [
        format_event(event, ISO_FORMAT) for event in formatted_calendar
    ]

    combined_events: List[CalendarEvent] = buffer_events
    combined_events.extend(
        event for event in calendar_events if event not in buffer_events
    )

    return [format_event(event, TIME_FORMAT) for event in combined_events]


def combine_issues(
    nvim: Nvim, markdown_issues: List[GitHubIssue], api_issues: List[GitHubIssue]
) -> List[GitHubIssue]:
    """combine_issues

    Takes both markdown and GitHub API issues and combines them.

    Treats the GitHub version as the truth, and keeps around any issues with an
    edit or new tag.
    """

    # Default to using the API version.
    combined_issues: List[GitHubIssue] = api_issues

    # Then, copy over any issues/comments with a new/edit tag, or that are missing.
    for issue in markdown_issues:
        api_issue_index: Optional[int] = get_issue_index(api_issues, issue.number)

        # If the issue doesn't exist at all, we need to add the whole thing.
        if api_issue_index is None:
            combined_issues.append(issue)
            continue

        api_issue: GitHubIssue = combined_issues[api_issue_index]

        # Add the new/edited comments
        for index, comment in enumerate(issue.all_comments):
            if len(api_issue.all_comments) <= index:
                api_issue.all_comments.append(comment)

                continue

            api_comment: GitHubIssueComment = api_issue.all_comments[index]

            # If we've got a new comment in the markdown, add it.
            if "new" in comment.tags:
                comment.number = len(api_issue.all_comments)
                api_issue.all_comments.append(comment)

                continue

            # If we've got an edited comment, where the online matches the
            # markdown version, keep the markdown comment around.
            if "edit" in comment.tags and comment.updated_at == api_comment.updated_at:
                api_issue.all_comments[index] = comment

                continue

            # If we've got an edited comment, where the online is newer than the
            # markdown version, add the markdown comment, but label it as conflicted.
            if "edit" in comment.tags and comment.updated_at < api_comment.updated_at:
                comment.number = len(api_issue.all_comments)
                comment.tags.append("conflict")

                api_issue.all_comments.append(comment)

    nvim.out_write(f"Updated {len(combined_issues) - len(markdown_issues)} issues.\n")

    return combined_issues
