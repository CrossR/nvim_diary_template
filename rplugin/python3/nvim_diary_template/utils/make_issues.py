"""make_issues

Functions to build and parse the issue section of the markdown.
"""
from typing import List

from neovim import Nvim

from ..classes.github_issue_class import (
    GitHubIssue,
    GitHubIssueComment,
)
from ..helpers.issue_helpers import check_markdown_style, sort_issues
from ..helpers.neovim_helpers import (
    get_buffer_contents,
    get_section_line,
)
from ..utils.constants import (
    EMPTY_TODO,
    HEADING_2,
    HEADING_3,
    ISSUE_HEADING,
    VIMWIKI_TODO,
)


def format_issues(issues: List[GitHubIssue]) -> List[str]:
    """format_issues

    Given some issues, will produce formatted lines for them.
    """

    issue_lines: List[str] = []
    sorted_issues: List[GitHubIssue] = sort_issues(issues)

    # For every issue, format it into markdown lines that are easily read.
    for issue in sorted_issues:

        issue_title: str = issue.title
        issue_comments: List[GitHubIssueComment] = issue.all_comments
        issue_number: int = issue.number
        issue_labels: List[str] = issue.labels
        issue_complete: bool = issue.complete
        issue_tags: List[str] = issue.metadata

        if issue_complete:
            issue_start = f"{HEADING_2} {VIMWIKI_TODO} Issue {{{issue_number}}}: "
        else:
            issue_start = f"{HEADING_2} {EMPTY_TODO} Issue {{{issue_number}}}: "

        title_line = f"{HEADING_3} Title: {issue_title}"

        # Apply the labels, and tags.
        for label in issue_labels:
            issue_start += f" +label:{label}"

        for tag in issue_tags:
            issue_start += f" +{tag}"

        formatted_comments: List[str] = format_issue_comments(issue_comments)

        issue_lines.append(issue_start.strip())
        issue_lines.append("")
        issue_lines.append(title_line)
        issue_lines.append("")
        issue_lines.extend(formatted_comments)

    return issue_lines


def format_issue_comments(comments: List[GitHubIssueComment]) -> List[str]:
    """format_issue_comments

    Formats each of the comments for a given issue, including the initial body
    of the comment. This includes adding padding and swapping newlines, as the
    nvim API does not allow this.
    """

    formatted_comments: List[str] = []

    for comment_num, comment in enumerate(comments):

        split_comments: List[str] = comment.body
        tags: List[str] = comment.tags
        comment_edit_time: str = comment.updated_at

        header_line = f"{HEADING_3} Comment {{{comment_num}}} - {comment_edit_time}:"

        # Apply the tags if there are any.
        for tag in tags:
            header_line += f" +{tag}"

        formatted_comments.append(header_line)

        # Format the lines of the comments.
        for line in split_comments:
            if line == "":
                formatted_comments.append("")
                continue

            processed_line: str = check_markdown_style(line, "vimwiki")
            formatted_comments.append(processed_line)

        formatted_comments.append("")

    return formatted_comments


def produce_issue_markdown(issue_list: List[GitHubIssue]) -> List[str]:
    """produce_issue_markdown

    Given a list of issues, will produce a basic bit of markdown
    to display those issues.
    """

    markdown_lines: List[str] = [ISSUE_HEADING, ""]

    issue_lines: List[str] = format_issues(issue_list)
    markdown_lines.extend(issue_lines)

    return markdown_lines


def remove_tag_from_issues(
    issues: List[GitHubIssue], tag: str, scope: str = "all"
) -> List[GitHubIssue]:
    """remove_tag_from_issues

    Removes all of a tag from the given issues.
    If scoped to just issues, we still check the first comment as this
    comment is the issue body.
    """

    for issue in issues:

        if scope == "all" or "issues":
            if tag in issue.metadata:
                issue.metadata.remove(tag)
                if tag in issue.all_comments[0].tags:
                    issue.all_comments[0].tags.remove(tag)

        if scope == "all" or "comments":
            for comment in issue.all_comments:
                if tag in comment.tags:
                    comment.tags.remove(tag)

    return issues


def set_issues_from_issues_list(nvim: Nvim, issues: List[GitHubIssue]) -> None:
    """set_issues_from_issues_list

    Update the issues for the current buffer with a new list of issues.
    """

    # Get the formatted lines to set.
    issue_lines: List[str] = format_issues(issues)

    buffer_number: int = nvim.current.buffer.number
    current_buffer: List[str] = get_buffer_contents(nvim)

    # We want the line after, as this gives the line of the heading.
    # Then add one to the end to replace the newline, as we add one.
    old_issues_start_line: int = get_section_line(current_buffer, ISSUE_HEADING) + 1

    old_issues_end_line: int = old_issues_start_line + len(issue_lines)

    nvim.api.buf_set_lines(
        buffer_number, old_issues_start_line, old_issues_end_line, True, issue_lines
    )
