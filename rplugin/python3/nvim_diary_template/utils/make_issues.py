"""make_issues

Functions to build and parse the issue section of the markdown.
"""

from nvim_diary_template.utils.constants import (BULLET_POINT, EMPTY_TODO,
                                                 TIME_FORMAT, TODO_HEADING)


def format_issues(issues):
    """format_issues

    Given some issues, will produce formatted lines for them.
    """

    issue_lines = []

    for issue in issues:

        issue_title = issue['title']
        issue_comments = issue['comments']

        # TODO: Similarly, make this string into a config option.
        # TODO: We are missing the issue body.
        # TODO: Add comment number.
        title_line = f"{BULLET_POINT} {EMPTY_TODO} {issue_title}"

        formatted_comments = format_issue_comments(issue_comments)

        issue_lines.append(title_line)
        issue_lines.extend(formatted_comments)

    issue_lines.append("")

    return issue_lines


def format_issue_comments(comments):
    """format_issue_comments

    Formats each of the comments for a given issue.
    This includes adding padding, swapping newlines (as the nvim API does not
    allow this) and splitting the lines as needed.
    """

    formatted_comments = []

    for comment in comments:
        split_comments = comment.splitlines()
        padded_comments = [
            f"     {comment_body}" if comment_body != ''
            else ''
            for comment_body in split_comments[1:]
        ]

        first_line = f"    {BULLET_POINT} {split_comments[0]}"

        formatted_comments.append(first_line)
        formatted_comments.extend(padded_comments)

    return formatted_comments


def produce_issue_markdown(issue_list):
    """produce_issue_markdown

    Given a list of issues, will produce a basic bit of markdown
    to display those issues.
    """

    markdown_lines = []

    # TODO: Should probably swap this to be a config option,
    # something like f"{importance * #}".
    markdown_lines.append(TODO_HEADING)

    issue_lines = format_issues(issue_list)
    markdown_lines.extend(issue_lines)

    return markdown_lines
