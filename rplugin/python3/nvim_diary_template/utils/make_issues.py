"""make_issues

Functions to build and parse the issue section of the markdown.
"""
from typing import Dict, List, Optional, Union

from neovim import Nvim

from ..classes.github_issue_class import GitHubIssue, GitHubIssueComment
from ..classes.plugin_options import PluginOptions
from ..helpers.issue_helpers import check_markdown_style, sort_issues
from ..helpers.neovim_helpers import get_buffer_contents, get_section_line
from ..utils.constants import (
    EMPTY_TODO,
    HEADING_3,
    HEADING_4,
    ISSUE_HEADING,
    SCHEDULE_HEADING,
    VIMWIKI_TODO,
)


def format_issues(
    options: PluginOptions, issues: List[GitHubIssue], should_sort: bool
) -> List[str]:
    """format_issues

    Given some issues, will produce formatted lines for them.
    """

    issue_lines: List[str] = []

    if should_sort:
        issues = sort_issues(options, issues)

    # For every issue, format it into markdown lines that are easily read.
    for issue in issues:

        if issue.complete:
            issue_start = f"{HEADING_3} {VIMWIKI_TODO} Issue {{{issue.number}}}:"
        else:
            issue_start = f"{HEADING_3} {EMPTY_TODO} Issue {{{issue.number}}}:"

        title_line = f"{HEADING_4} Title: {issue.title}"

        # Apply the labels, and tags.
        for label in issue.labels:
            issue_start += f" +label:{label}"

        for tag in issue.metadata:
            issue_start += f" +{tag}"

        formatted_comments: List[str] = format_issue_comments(issue.all_comments)

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

        header_line = f"{HEADING_4} Comment {{{comment_num}}} - {comment.updated_at}:"

        # Apply the tags if there are any.
        for tag in comment.tags:
            header_line += f" +{tag}"

        formatted_comments.append(header_line)

        # Format the lines of the comments.
        for line in comment.body:
            if line == "":
                formatted_comments.append("")
                continue

            processed_line: str = check_markdown_style(line, "vimwiki")
            formatted_comments.append(processed_line)

        formatted_comments.append("")

    return formatted_comments


def produce_issue_markdown(
    options: PluginOptions, issue_list: List[GitHubIssue]
) -> List[str]:
    """produce_issue_markdown

    Given a list of issues, will produce a basic bit of markdown
    to display those issues.
    """

    markdown_lines: List[str] = [ISSUE_HEADING, ""]

    issue_lines: List[str] = format_issues(options, issue_list, True)
    markdown_lines.extend(issue_lines)

    return markdown_lines


def remove_tag_from_issues(
    issues: List[GitHubIssue],
    tag: str,
    scope: str = "all",
    ignore_list: Optional[Union[List[int], List[Dict[str, int]]]] = None,
) -> List[GitHubIssue]:
    """remove_tag_from_issues

    Removes all of a tag from the given issues.
    If scoped to just issues, we still check the first comment as this
    comment is the issue body.
    """

    if ignore_list is None:
        ignore_list = [-1]

    for index, issue in enumerate(issues):

        if scope in ("all", "issues"):
            if tag in issue.metadata:

                # If the issue is one we should ignore, continue.
                # This is usually due to the issue being empty.
                if index in ignore_list:
                    continue

                issue.metadata.remove(tag)
                if tag in issue.all_comments[0].tags:
                    issue.all_comments[0].tags.remove(tag)

        if scope in ("all", "comments"):
            for comment in issue.all_comments:
                if tag in comment.tags:

                    # If the comment is one we should ignore, continue.
                    # This is usually due to the comment being empty.
                    if {"issue": index, "comment": comment.number} in ignore_list:
                        continue

                    comment.tags.remove(tag)

    return issues


def set_issues_from_issues_list(
    nvim: Nvim, options: PluginOptions, issues: List[GitHubIssue], should_sort: bool
) -> None:
    """set_issues_from_issues_list

    Update the issues for the current buffer with a new list of issues.
    """

    # Get the formatted lines to set.
    issue_lines: List[str] = format_issues(options, issues, should_sort)

    buffer_number: int = nvim.current.buffer.number
    current_buffer: List[str] = get_buffer_contents(nvim)

    # We want the line after, as this gives the line of the heading.
    # Then add one to the end to replace the newline, as we add one.
    old_issues_start_line: int = get_section_line(current_buffer, ISSUE_HEADING) + 1

    old_issues_end_line: int = get_section_line(current_buffer, SCHEDULE_HEADING) - 1

    nvim.api.buf_set_lines(
        buffer_number, old_issues_start_line, old_issues_end_line, True, issue_lines
    )
