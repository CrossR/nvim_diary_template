"""issue_helpers

Simple helpers to deal with Github issues.
"""
import re
from datetime import datetime
from typing import Any, Dict, List, Tuple, Union, Optional

from dateutil import tz
from neovim import Nvim

from ..classes.github_issue_class import GitHubIssue, GitHubIssueComment
from ..helpers.neovim_helpers import (
    get_buffer_contents,
    get_section_line,
    set_line_content,
)
from ..utils.constants import (
    EMPTY_TODO,
    GITHUB_TODO,
    HEADING_3,
    HEADING_4,
    ISSUE_COMMENT,
    ISSUE_HEADING,
    ISSUE_START,
    SCHEDULE_HEADING,
    TODO_IN_PROGRESS_REGEX,
    VIMWIKI_TODO,
)


def insert_edit_tag(nvim: Nvim, location: str) -> None:
    """insert_edit_tag

    Insert an edit tag for the current issue or comment, so it can be updated.
    """

    # Grab the indexes needed to find the issue we are in.
    current_line: int = nvim.current.window.cursor[0]
    current_buffer: List[str] = get_buffer_contents(nvim)
    issues_header_index: int = get_section_line(current_buffer, ISSUE_HEADING)
    schedule_header_index: int = get_section_line(current_buffer, SCHEDULE_HEADING) - 1

    inside_issues_section: bool = issues_header_index <= current_line <= schedule_header_index

    # If we are outside the issues section, return.
    if not inside_issues_section:
        return

    relevant_buffer: List[str] = current_buffer[issues_header_index:current_line]
    line_index: int = -1

    if location == "issue":
        target_line: str = ISSUE_START
    elif location == "comment":
        target_line = ISSUE_COMMENT
    else:
        raise ValueError(f"{location} is not a recognised target.")

    # Search the buffer backwards and find the start of the current target, to
    # get its line index.
    for index in range(len(relevant_buffer) - 1, 0, -1):
        line: str = relevant_buffer[index]
        if re.findall(target_line, line):
            line_index = index

            break

    # If we didn't find the target, return since we can't update it.
    if line_index == -1:
        return

    # If we did find a line, we want to append +edit to the end, and set it.
    # We need to update the line index to be relative to the full buffer.
    updated_line: str = relevant_buffer[line_index]
    updated_line += " +edit"

    insert_index: int = issues_header_index + line_index + 1

    set_line_content(nvim, [updated_line], line_index=insert_index, line_offset=1)


def insert_new_issue(nvim: Nvim) -> None:
    """insert_new_issue

    Find the issue that the cursor is currently inside of, and get the next
    issue number. Then insert a new issue at the correct place with this
    number.
    """

    # Grab the indexes needed to find the issue we are in.
    current_buffer: List[str] = get_buffer_contents(nvim)
    schedule_header_index: int = get_section_line(current_buffer, SCHEDULE_HEADING) - 1

    new_line_number: int = schedule_header_index

    issue_start: str = f"{HEADING_3} {EMPTY_TODO} Issue {{00}}: +new"
    title_line: str = f"{HEADING_4} Title: "
    comment_line: str = f"{HEADING_4} Comment {{0}} - 0000-00-00 00:00: +new"

    new_comment: List[str] = ["", issue_start, "", title_line, "", comment_line]

    set_line_content(nvim, new_comment, line_index=new_line_number)

    new_cursor_pos: Tuple[int, int] = (new_line_number + 3, len(title_line) - 1)
    nvim.current.window.cursor = new_cursor_pos


def insert_new_comment(nvim: Nvim) -> None:
    """insert_new_comment

    Find the issue that the cursor is currently inside of, and get the next
    comment number. Then insert a new comment at the correct place with this
    number.
    """

    # Grab the indexes needed to find the issue we are in.
    current_line: int = nvim.current.window.cursor[0]
    current_buffer: List[str] = get_buffer_contents(nvim)
    issues_header_index: int = get_section_line(current_buffer, ISSUE_HEADING)
    schedule_header_index: int = get_section_line(current_buffer, SCHEDULE_HEADING) - 1

    inside_issues_section: bool = issues_header_index <= current_line <= schedule_header_index

    # If we are outside the issues section, return.
    if not inside_issues_section:
        return

    relevant_buffer: List[str] = current_buffer[current_line:schedule_header_index]
    new_line_number: int = 0

    # Search the buffer forwards and find the start of the next issue, to
    # insert before it. Then, find the last comment number and increment it.
    for index, line in enumerate(relevant_buffer):
        if re.findall(ISSUE_START, line):
            new_line_number = index

            break

    # If we didn't change the new line number, we must be in the last comment.
    # Instead, just place above the next section heading.
    if new_line_number == 0:
        new_line_number = schedule_header_index

    relative_line: int = current_line + new_line_number
    relevant_buffer = current_buffer[issues_header_index:relative_line]
    comment_number: int = -1

    # Search back to find the latest comment number, so we can increment it.
    for line in reversed(relevant_buffer):
        if re.findall(ISSUE_COMMENT, line):
            comment_number = int(re.findall(r"\d+", line)[0])

            break

    # If we didn't find a comment number to use, we should probably quit.
    if comment_number == -1:
        return

    # Add a new issue comment line, and set the line, before moving the cursor
    # there.
    header_line: str = (
        f"{HEADING_4} Comment {{{comment_number + 1}}} - 0000-00-00 00:00: +new"
    )
    new_comment: List[str] = ["", header_line, ""]

    set_line_content(nvim, new_comment, line_index=relative_line)

    new_cursor_pos: Tuple[int, int] = (relative_line + 2, 0)
    nvim.current.window.cursor = new_cursor_pos


def toggle_issue_completion(nvim: Nvim) -> None:
    """toggle_issue_completion

    Finds the current issue, and toggles its completion status.
    """

    # Grab the indexes needed to find the issue we are in.
    current_line: int = nvim.current.window.cursor[0]
    current_buffer: List[str] = get_buffer_contents(nvim)
    issues_header_index: int = get_section_line(current_buffer, ISSUE_HEADING)
    schedule_header_index: int = get_section_line(current_buffer, SCHEDULE_HEADING) - 1

    inside_issues_section: bool = issues_header_index <= current_line <= schedule_header_index

    # If we are outside the issues section, return.
    if not inside_issues_section:
        return

    relevant_buffer: List[str] = current_buffer[issues_header_index:current_line]
    line_index: int = -1

    target_line: str = ISSUE_START

    # Search the buffer backwards and find the start of the current issue, to
    # get its line index.
    for index in range(len(relevant_buffer) - 1, 0, -1):
        line: str = relevant_buffer[index]
        if re.findall(target_line, line):
            line_index = index

            break

    # If we didn't find the target, return since we can't update it.
    if line_index == -1:
        return

    # If we did find an issue, we want to toggle the completion status.
    # We need to update the line index to be relative to the full buffer.
    current_issue: str = relevant_buffer[line_index]

    if re.findall(re.escape(EMPTY_TODO), current_issue):
        updated_line: str = current_issue.replace(EMPTY_TODO, VIMWIKI_TODO)
    elif re.findall(re.escape(VIMWIKI_TODO), current_issue):
        updated_line = current_issue.replace(VIMWIKI_TODO, EMPTY_TODO)

    insert_index: int = issues_header_index + line_index + 1

    set_line_content(nvim, [updated_line], line_index=insert_index, line_offset=1)


def check_markdown_style(line: str, desired_style: str) -> str:
    """check_markdown_style

    Given a line, check that the style is consistent with what that platform expects.
    Ie, GitHub uses [x] which Vimwiki doesn't recognise, so swap that to [X].

    desired_style should be 'vimwiki' or 'github'.
    """

    if desired_style == "vimwiki":
        return github_to_vimwiki_process(line)

    if desired_style == "github":
        return vimwiki_to_github_process(line)

    raise Exception("Unknown style.")


def vimwiki_to_github_process(line: str) -> str:
    """vimwiki_to_github_process

    Convert VimWiki markdown to Github style.

    Currently, this means swapping [X] to [x] and removing all intermidate
    states from todo checkboxes, like [o]
    """

    # If we have some vimwiki style checked todos, replace them.
    if re.findall(re.escape(VIMWIKI_TODO), line):
        line = line.replace(VIMWIKI_TODO, GITHUB_TODO)

    # If we have some vimwiki style in-progress todos, replace them.
    if re.findall(TODO_IN_PROGRESS_REGEX, line):
        line = re.sub(TODO_IN_PROGRESS_REGEX, EMPTY_TODO, line)

    return line


def github_to_vimwiki_process(line: str) -> str:
    """github_to_vimwiki_process

    Convert Github markdown to Vimwiki style.

    Currently, this means swapping [x] to [X].
    """

    # If we have some Github style checked todos, replace them.
    if re.findall(re.escape(GITHUB_TODO), line):
        line = line.replace(GITHUB_TODO, VIMWIKI_TODO)

    return line


def convert_utc_timezone(passed_datetime: datetime, target: str) -> str:
    """convert_utc_timezone

    Converts the UTC timezone Object into the correct timezone string.
    The target should be a timezone string.
    """

    utc_time: datetime = passed_datetime.replace(tzinfo=tz.tzutc())

    return utc_time.astimezone(tz.gettz(target)).strftime("%Y-%m-%d %H:%M")


def sort_issues(issues: List[GitHubIssue]) -> List[GitHubIssue]:
    """sort_issues

    A helper function to sort the given issues.
    The sorting works as follows:
    - Complete issues have the lowest priority.
    - Backlog issues have low priority.
    - Blocked issues have low priority.
    - In-progress issues have the highest priority.
    - The latest edit is used for any ties, with issue number being used in
    the case of a tie there.
    """

    return sorted(
        issues,
        key=lambda i: (
            sort_completion_state(i),
            i.all_comments[-1].updated_at,
            i.number,
        ),
    )


def sort_completion_state(issue: GitHubIssue) -> int:
    """sort_completion_state

    Simple helper function to return a value for the issue current state for
    sorting.

    The higher the value, the lower they will be on the list.
    """

    if issue.complete:
        return 10000

    if "backlog" in issue.labels:
        return 5000

    if "blocked" in issue.labels:
        return 1000

    if "inprogress" in issue.labels:
        return 0

    return 100


def get_github_objects(
    issues: Union[List[GitHubIssue], List[Dict[str, Any]]]
) -> List[GitHubIssue]:
    """get_github_objects

    Convert the loaded dicts to Objects, if they are not already.
    This is easier for a number of reasons, the main of which is
    that naming is kept consistent, versus dicts which require more
    careful usage.
    """

    issues_to_convert: List[Dict[str, Any]] = [
        issue for issue in issues if isinstance(issue, dict)
    ]

    # TODO: Update this to use `is_dataclass` when we swap to Python 3.7
    issue_objects: List[GitHubIssue] = [
        issue for issue in issues if not isinstance(issue, dict)
    ]

    for issue in issues_to_convert:
        current_comments: List[GitHubIssueComment] = []

        for comment in issue["all_comments"]:
            current_comments.append(GitHubIssueComment(**comment))

        issue_objects.append(
            GitHubIssue(
                number=issue["number"],
                title=issue["title"],
                complete=issue["complete"],
                labels=issue["labels"],
                all_comments=current_comments,
                metadata=[],
            )
        )

    return issue_objects


def split_comment(comment: str) -> List[str]:
    """split_comment

    Splits a comment into an array of lines.
    Broadly, this just wraps the .splitlines() function,
    such that the leading and trailing newlines can be removed.
    """

    lines: List[str] = comment.splitlines()

    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    return lines


def get_issue_index(issues: List[GitHubIssue], target_number: int) -> Optional[int]:
    """get_issue_index

    Get the index of a given issue in a list, or return None if it does not exist.
    """

    target_index: Optional[int] = None

    for index, issue in enumerate(issues):
        if issue.number == target_number:
            target_index = index

    return target_index
