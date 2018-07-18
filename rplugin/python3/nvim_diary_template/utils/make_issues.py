"""make_issues

Functions to build and parse the issue section of the markdown.
"""

from nvim_diary_template.helpers.neovim_helpers import (get_buffer_contents,
                                                        get_section_line)
from nvim_diary_template.utils.constants import (BULLET_POINT, EMPTY_TODO,
                                                 ISSUE_HEADING, PADDING)


def format_issues(issues):
    """format_issues

    Given some issues, will produce formatted lines for them.
    """

    issue_lines = []

    # For every issue, format it into markdown lines that are easily read.
    for issue in issues:

        issue_title = issue['title']
        issue_comments = issue['all_comments']
        issue_number = issue['number']

        # TODO: Similarly, make this string into a config option.
        issue_start = f"{BULLET_POINT} {EMPTY_TODO} Issue {{{issue_number}}}:"
        title_line = f"{PADDING}{BULLET_POINT} Title: {issue_title}"

        try:
            tags = issue['metadata']

            for tag in tags:
                issue_start += f" +{tag}"
        except KeyError:
            continue

        formatted_comments = format_issue_comments(issue_comments)

        issue_lines.append(issue_start)
        issue_lines.append(title_line)
        issue_lines.append('')
        issue_lines.extend(formatted_comments)

    return issue_lines


def format_issue_comments(comments):
    """format_issue_comments

    Formats each of the comments for a given issue, including the initial body
    of the comment.  This includes adding padding and swapping newlines, as the
    nvim API does not allow this.
    """

    formatted_comments = []
    add_new_line = True

    for comment_num, comment in enumerate(comments):

        tags = []

        # If we've passed over a dict, for example after parsing the file, we
        # need to access the comments differently, and not apply a new line.
        if isinstance(comment, dict):
            split_comments = comment['comment_lines']
            tags = comment['comment_tags']
            add_new_line = False
        else:
            split_comments = comment.splitlines()

        # TODO: Pass over metadata for this header line for the non-dict.
        header_line = f"{PADDING}{BULLET_POINT} Comment {{{comment_num}}}:"

        for tag in tags:
            header_line += f" +{tag}"

        formatted_comments.append(header_line)

        for line in split_comments:
            if line == '':
                formatted_comments.append('')
                continue

            current_line = f"{PADDING * 2}{line}"
            formatted_comments.append(current_line)

        if add_new_line:
            formatted_comments.append('')

    return formatted_comments


def produce_issue_markdown(issue_list):
    """produce_issue_markdown

    Given a list of issues, will produce a basic bit of markdown
    to display those issues.
    """

    markdown_lines = []

    # TODO: Should probably swap this to be a config option,
    # something like f"{importance * #}".
    markdown_lines.append(ISSUE_HEADING)
    markdown_lines.append('')

    issue_lines = format_issues(issue_list)
    markdown_lines.extend(issue_lines)

    return markdown_lines


def remove_tag_from_comments(issues, tag):
    """remove_tag_from_comments

    Removes all of a tag from comments.
    """

    for issue in issues:
        for comment in issue['all_comments']:
            if tag in comment['comment_tags']:
                comment['comment_tags'].remove(tag)

    return issues


def set_issues_from_issues_list(nvim, issues):
    """set_issues_from_issues_list

    Update the issues for the current buffer with a new list of issues.
    """

    # Get the formatted lines to set.
    issue_lines = format_issues(issues)

    buffer_number = nvim.current.buffer.number
    current_buffer = get_buffer_contents(nvim)

    # We want the line after, as this gives the line of the heading.
    # Then add one to the end to replace the newline, as we add one.
    old_issues_start_line = get_section_line(
        current_buffer,
        ISSUE_HEADING
    ) + 1

    old_issues_end_line = old_issues_start_line + len(issue_lines)

    nvim.api.buf_set_lines(
        buffer_number,
        old_issues_start_line,
        old_issues_end_line,
        True,
        issue_lines
    )
