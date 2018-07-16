"""issue_helpers

Simple helpers to deal with Github issues.
"""
import re

from nvim_diary_template.helpers.neovim_helpers import (get_buffer_contents,
                                                        get_section_line,
                                                        set_line_content)
from nvim_diary_template.utils.constants import (BULLET_POINT, ISSUE_COMMENT,
                                                 ISSUE_HEADING, ISSUE_TITLE,
                                                 PADDING, SCHEDULE_HEADING)


def convert_issues(github_service, issue_list):
    """convert_issues

    Given a basic list of issues, grab the associated comments for printing.
    """

    formatted_issues = []

    for issue in issue_list:
        comments = github_service.get_comments_for_issue(issue['number'])
        formatted_issues.append({
            'number': issue['number'],
            'title': issue['title'],
            'body': issue['body'],
            'comments': comments,
        })

    return formatted_issues


def insert_new_comment(nvim):
    """insert_new_comment

    Find the issue that the cursor is currently inside of, and get the next
    comment number. Then insert a new comment at the correct place with this
    number.
    """

    current_line = nvim.current.window.cursor[0]
    current_buffer = get_buffer_contents(nvim)
    issues_header_index = get_section_line(current_buffer, ISSUE_HEADING)
    schedule_header_index = get_section_line(
        current_buffer, SCHEDULE_HEADING) - 1

    inside_issues_section = (current_line >= issues_header_index and
                             current_line <= schedule_header_index)

    # If we are outside the issues section, return.
    if not inside_issues_section:
        return

    relevant_buffer = current_buffer[current_line:schedule_header_index]
    new_line_number = 0

    # Search the buffer forwards and find the start of the next comment, to
    # insert before it. Then, find the last comment number and increment it.
    for index, line in enumerate(relevant_buffer):
        if re.findall(ISSUE_TITLE, line):
            new_line_number = index - 1

            break

    # If we didn't change the new line number, we must be in the last comment.
    # Instead, just place above the next heading.
    if new_line_number == 0:
        new_line_number = schedule_header_index

    relevant_buffer = current_buffer[issues_header_index:new_line_number]
    comment_number = 99

    # Search back to find the latest comment number.
    for line in reversed(relevant_buffer):
        if re.findall(ISSUE_COMMENT, line):
            comment_number = int(re.findall(r"\d+", line)[0])

            break

    header_line = f"{PADDING}{BULLET_POINT} Comment {{{comment_number + 1}}}: +new"
    new_comment = ['', header_line]
    set_line_content(nvim, new_comment, line_index=new_line_number)
    nvim.err_write(f"{new_line_number}, {current_line}\n")
