"""parse_markdown

Functions for the parsing of the document markdown.
"""

import re
from datetime import date

from dateutil import parser

from nvim_diary_template.helpers.event_helpers import format_event
from nvim_diary_template.helpers.google_calendar_helpers import convert_events
from nvim_diary_template.helpers.neovim_helpers import (get_buffer_contents,
                                                        get_section_line,
                                                        set_line_content)
from nvim_diary_template.utils.constants import (DATETIME_REGEX, EVENT_REGEX,
                                                 ISO_FORMAT, ISSUE_COMMENT,
                                                 ISSUE_HEADING, ISSUE_METADATA,
                                                 ISSUE_START, ISSUE_TITLE,
                                                 PADDING_SIZE,
                                                 SCHEDULE_HEADING, TIME_FORMAT,
                                                 TIME_REGEX, TODO_IS_CHECKED)


def parse_buffer_events(events, format_string):
    """parse_buffer_events

    Given a list of events, parse the buffer lines and create event objects.
    """

    formatted_events = []

    for event in events:
        if event == '':
            continue

        # TODO: Regex is probably going to be a giant pain here,
        # and won't work if the string pattern changes.
        matches_date_time = re.findall(DATETIME_REGEX, event)

        if not matches_date_time:
            matches_time = re.findall(TIME_REGEX, event)
            start_date = parser.parse(matches_time[0]) \
                               .strftime(format_string)
            end_date = parser.parse(matches_time[1]) \
                             .strftime(format_string)
        else:
            start_date = parser.parse(matches_date_time[0]) \
                               .strftime(format_string)
            end_date = parser.parse(matches_date_time[1]) \
                             .strftime(format_string)

        event_details = re.search(EVENT_REGEX, event)[0]

        event_dict = {
            'event_name': event_details,
            'start_time': start_date,
            'end_time': end_date
        }

        formatted_events.append(event_dict)

    return formatted_events


def parse_buffer_issues(issue_lines):
    """parse_buffer_issues

    Given a list of issue markdown lines, parse the issue lines and create
    issue objects.
    """

    formatted_issues = []
    issue_number = -1
    comment_number = -1

    for line in issue_lines:
        is_issue_start = re.findall(ISSUE_START, line)
        is_issue_title = re.findall(ISSUE_TITLE, line)
        is_comment_start = re.findall(ISSUE_COMMENT, line)

        # If its the start of a new issue, add a new object.
        # Reset the comment number.
        if is_issue_start:
            issue_number += 1
            comment_number = -1
            metadata = re.findall(ISSUE_METADATA, line)

            # Strip the leading '+' from the tags.
            metadata = [
                tag[1:] for tag in metadata
            ]

            formatted_issues.append({
                'number': int(re.findall(r"\d+", line)[0]),
                'title': '',
                'metadata': metadata,
                'complete': re.search(TODO_IS_CHECKED, line) != None,
                'all_comments': [],
            })

            continue

        # If its the issue title, then add that to the empty object.
        if is_issue_title:
            issue_title = re.sub(ISSUE_TITLE, '', line).strip()

            formatted_issues[issue_number]['title'] = issue_title

            continue

        # If this is a comment, start to add it to the existing object.
        if is_comment_start:
            comment_number = int(re.findall(r"\d+", line)[0])
            comment_metadata = re.findall(ISSUE_METADATA, line)

            # Strip the leading '+' from the tags.
            comment_metadata = [
                tag[1:] for tag in comment_metadata
            ]

            formatted_issues[issue_number]['all_comments'].append({
                'comment_number': comment_number,
                'comment_tags': comment_metadata,
                'comment_lines': [],
            })

            continue

        # Finally, if there is an issue and comment ongoing, we can add to the
        # current comment.
        if issue_number != -1 and comment_number != -1:
            stripped_line = line[PADDING_SIZE * 2:]
            current_issue = formatted_issues[issue_number]['all_comments']
            current_comment = current_issue[comment_number]['comment_lines']
            current_comment.append(stripped_line)

    return formatted_issues


def remove_events_not_from_today(nvim):
    """remove_events_not_from_today

    Remove events from the file if they are not for the correct date.
    """

    current_events = parse_markdown_file_for_events(nvim, ISO_FORMAT)
    date_today = date.today()
    schedule_index = get_section_line(
        get_buffer_contents(nvim),
        SCHEDULE_HEADING
    ) + 1

    for index, event in enumerate(current_events):
        event_date = parser.parse(event['start_time']).date()

        if date_today == event_date:
            continue

        event_index = schedule_index + index + 1

        set_line_content(nvim, [""], event_index)


def parse_markdown_file_for_events(nvim, format_string):
    """parse_markdown_file_for_events

    Gets the contents of the current NeoVim buffer,
    and parses the schedule section into events.
    """

    current_buffer = get_buffer_contents(nvim)

    buffer_events_index = get_section_line(current_buffer, SCHEDULE_HEADING)
    events = current_buffer[buffer_events_index:]
    formatted_events = parse_buffer_events(events, format_string)

    return formatted_events


def parse_markdown_file_for_issues(nvim):
    """parse_markdown_file_for_issues

    Gets the contents of the current NeoVim buffer,
    and parses the issues section into issues.
    """

    current_buffer = get_buffer_contents(nvim)

    # Get the start of each section, to grab the lines between. We plus one to
    # the issues header, to skip the empty line there. We remove two from the
    # events header to remove both the Events header itself, as well as the
    # empty line at the end of the issues section.
    buffer_issues_index = get_section_line(current_buffer, ISSUE_HEADING) + 1
    buffer_events_index = get_section_line(
        current_buffer, SCHEDULE_HEADING) - 2

    issues = current_buffer[buffer_issues_index:buffer_events_index]
    formatted_issues = parse_buffer_issues(issues)

    return formatted_issues


def combine_events(markdown_events,
                   google_events):
    """combine_events

    Takes both markdown and google events and combines them into a single list,
    with no duplicates.

    The markdown is taken to be the ground truth, as there is no online copy.
    """

    buffer_events = [
        format_event(event, ISO_FORMAT) for event in markdown_events
    ]

    formatted_calendar = convert_events(google_events, ISO_FORMAT)
    calendar_events = [
        format_event(event, ISO_FORMAT) for event in formatted_calendar
    ]

    combined_events = buffer_events
    combined_events.extend(
        event for event in calendar_events if event not in buffer_events
    )

    return [
        format_event(event, TIME_FORMAT) for event in combined_events
    ]
