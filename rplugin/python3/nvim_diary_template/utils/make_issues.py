"""make_issues

Functions to build and parse the issue section of the markdown.
"""

from nvim_diary_template.utils.constants import (BULLET_POINT, EMPTY_TODO,
                                                 ISSUE_HEADING, PADDING)


def format_issues(issues):
    """format_issues

    Given some issues, will produce formatted lines for them.
    """

    issue_lines = []

    for issue in issues:

        issue_title = issue['title']
        issue_comments = issue['comments']
        issue_body = issue['body']

        # TODO: Similarly, make this string into a config option.
        title_line = f"{BULLET_POINT} {EMPTY_TODO} {issue_title}"

        formatted_comments = format_issue_comments(issue_body, issue_comments)

        issue_lines.append(title_line)
        issue_lines.extend(formatted_comments)

    return issue_lines


def format_issue_comments(body, comments):
    """format_issue_comments

    Formats each of the comments for a given issue, including the initial body
    of the comment.  This includes adding padding and swapping newlines, as the
    nvim API does not allow this.
    """

    formatted_comments = []

    joint_body_and_comments = [body] + comments

    for comment_num, comment in enumerate(joint_body_and_comments):
        split_comments = comment.splitlines()

        # TODO: Pass over metadata for this header line. Mainly date/time.
        header_line = f"{PADDING}{BULLET_POINT} Comment {{{comment_num}}}:"
        formatted_comments.append(header_line)

        for line in split_comments:
            if line == '':
                formatted_comments.append('')
                continue

            current_line = f"{PADDING * 2}{line}"
            formatted_comments.append(current_line)

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
