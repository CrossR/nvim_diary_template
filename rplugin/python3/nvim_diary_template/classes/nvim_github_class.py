# pylint: disable=invalid-name
"""nvim_github_class

The Github class, with Neovim options to log information
back to the user.
"""

import json
from os import path
from typing import Any, Dict, List, Optional, Tuple, Union

from github import Github
from neovim import Nvim

from ..classes.github_issue_class import GitHubIssue, GitHubIssueComment
from ..classes.plugin_options import PluginOptions
from ..helpers.file_helpers import check_cache
from ..helpers.issue_helpers import (
    check_markdown_style,
    convert_utc_timezone,
    get_github_objects,
    split_comment,
)
from ..helpers.neovim_helpers import buffered_info_message
from ..utils.constants import (
    ISSUE_CACHE_DURATION,
    LABELS_CACHE_DURATION,
    REPO_CACHE_DURATION,
)


class SimpleNvimGithub:
    """SimpleNvimGithub

    A class to deal with the simple interactions with the Github API.
    """

    def __init__(self, nvim: Nvim, options: PluginOptions) -> None:
        self.nvim: Nvim = nvim
        self.config_path: str = options.config_path
        self.repo_name: str = options.repo_name
        self.options: PluginOptions = options

        self.service: Optional[Github] = self.setup_github_api()

        if self.service_not_valid():
            return

        loaded_issues: Union[List[Dict[str, Any]], List[GitHubIssue]] = check_cache(
            self.config_path,
            "open_issues",
            ISSUE_CACHE_DURATION,
            self.get_all_open_issues,
        )

        self.issues: List[GitHubIssue] = get_github_objects(loaded_issues)

        check_cache(
            self.config_path, "repo_labels", LABELS_CACHE_DURATION, self.get_repo_labels
        )

        check_cache(
            self.config_path,
            "user_repos",
            REPO_CACHE_DURATION,
            self.get_associated_repos,
        )

    @property
    def active(self) -> bool:
        """active

        Is the Github service active?
        """
        return not self.service_not_valid()

    def setup_github_api(self) -> Optional[Github]:
        """setup_github_api

            Sets up the initial Github service, which can then be used
            for future work.
        """

        try:
            with open(
                path.join(self.config_path, "github_credentials.json")
            ) as json_file:
                store: Dict[str, str] = json.load(json_file)

            access_token: str = store["access_token"]
        except (IOError, ValueError):
            self.nvim.err_write(
                "Credentials invalid, try re-generating or checking the path.\n"
            )
            return None

        service: Github = Github(access_token)

        return service

    def service_not_valid(self) -> bool:
        """service_not_valid

        Check if the Github API service is ready.
        """
        if self.service is None:
            return True

        if self.repo_name == "":
            return True

        return False

    def get_repo_labels(self) -> List[str]:
        """get_repo_labels

        Get the labels for the current repo.
        """

        if self.service is None:
            self.nvim.err_write("Github service not currently running...\n")
            return []

        repo_labels: Any = self.service.get_repo(self.repo_name).get_labels()

        return [label.name for label in repo_labels]

    def get_associated_repos(self) -> List[str]:
        """get_associated_repos

        Get all the repos the current user is associated with.
        """

        if self.service is None:
            self.nvim.err_write("Github service not currently running...\n")
            return []

        if self.options.user_name == "":
            return []

        repos: Any = self.service.get_user(self.options.user_name).get_repos(type="all")

        return [repo.full_name for repo in repos]

    def get_all_open_issues(self) -> List[GitHubIssue]:
        """get_all_open_issues

        Returns a list of all the open issues, including all comments.
        """

        if self.service is None:
            self.nvim.err_write("Github service not currently running...\n")
            return []

        issues: Any = self.service.get_repo(self.repo_name).get_issues(state="open")

        issue_list: List[GitHubIssue] = []

        for issue in issues:

            initial_comment: GitHubIssueComment = GitHubIssueComment(
                number=0,
                body=split_comment(issue.body),
                tags=[],
                updated_at=convert_utc_timezone(
                    issue.updated_at, self.options.timezone
                ),
            )

            # Grab the comments for this issue too.
            all_comments: List[GitHubIssueComment] = self.format_comments(
                issue.get_comments()
            )

            issue_list.append(
                GitHubIssue(
                    number=issue.number,
                    complete=False,
                    title=issue.title,
                    all_comments=[initial_comment, *all_comments],
                    labels=[label.name for label in issue.labels],
                    metadata=[],
                )
            )

        return issue_list

    def format_comments(self, comments: List[Any]) -> List[GitHubIssueComment]:
        """format_comments

        Format all the comments that are passed into GitHubIssueComment
        objects.
        """

        comment_objs: List[GitHubIssueComment] = []

        current_comment: int = 1

        for comment in comments:
            comment_objs.append(
                GitHubIssueComment(
                    number=current_comment,
                    body=split_comment(comment.body),
                    tags=[],
                    updated_at=convert_utc_timezone(
                        comment.updated_at, self.options.timezone
                    ),
                )
            )

            current_comment += 1

        return comment_objs

    @staticmethod
    def filter_comments(
        issues: List[GitHubIssue], tag: str
    ) -> Tuple[List[GitHubIssue], List[Dict[str, int]]]:
        """filter_comments

        Filter comments for uploading, by a specific tag.
        """

        comments_to_upload: List[GitHubIssue] = []
        change_indexes: List[Dict[str, int]] = []

        # For every issue, check the comments and check if the tags for that
        # comment contain the target tag. If it does, setup an obj with some
        # needed value as well as storing the index of the comment, so it can
        # be updated later.
        for issue_index, issue in enumerate(issues):
            for comment_index, comment in enumerate(issue.all_comments):
                if tag in comment.tags:
                    comment_lines: List[str] = comment.body
                    processed_comment_lines: List[str] = [
                        check_markdown_style(line, "github") for line in comment_lines
                    ]

                    processed_comment: GitHubIssueComment = GitHubIssueComment(
                        number=comment.number,
                        body=["\r\n".join(processed_comment_lines)],
                        tags=comment.tags,
                        updated_at=comment.updated_at,
                    )

                    # Lets make an issue with 1 comment per issue, to simplify the code.
                    comments_to_upload.append(
                        GitHubIssue(
                            number=issue.number,
                            title=issue.title,
                            complete=issue.complete,
                            labels=issue.labels,
                            metadata=issue.metadata,
                            all_comments=[processed_comment],
                        )
                    )

                    change_indexes.append(
                        {"issue": issue_index, "comment": comment_index}
                    )

        return comments_to_upload, change_indexes

    @staticmethod
    def filter_issues(
        issues: List[GitHubIssue], tag: str
    ) -> Tuple[List[GitHubIssue], List[int]]:
        """filter_issues

        Filter issues for uploading, by a specific tag.
        """

        issues_to_upload: List[GitHubIssue] = []
        change_indexes: List[int] = []

        # For every issue, check the metadata to see if it contains the target
        # tag. If it does, setup an obj with some needed value as well as
        # storing the index of the issue, so it can be updated later.
        for index, issue in enumerate(issues):
            if tag in issue.metadata:
                comment: GitHubIssueComment = issue.all_comments[0]
                processed_body: List[str] = [
                    check_markdown_style(line, "github") for line in comment.body
                ]

                body_comment: GitHubIssueComment = GitHubIssueComment(
                    number=comment.number,
                    body=["\r\n".join(processed_body)],
                    tags=comment.tags,
                    updated_at=comment.updated_at,
                )

                issues_to_upload.append(
                    GitHubIssue(
                        number=issue.number,
                        title=issue.title,
                        complete=False,
                        labels=issue.labels,
                        all_comments=[body_comment],
                        metadata=issue.metadata,
                    )
                )

                change_indexes.append(index)

        return issues_to_upload, change_indexes

    def upload_comments(
        self, issues: List[GitHubIssue], tag: str
    ) -> Tuple[List[GitHubIssue], List[Dict[str, int]]]:
        """upload_comments

        Upload comments with the specific tag to GitHub.
        """

        if self.service is None:
            self.nvim.err_write("Github service not currently running...\n")
            return [], []

        comments_to_upload, change_indexes = self.filter_comments(issues, tag)
        comments_to_ignore: List[Dict[str, int]] = []
        change_count: int = 0

        for issue, change_index in zip(comments_to_upload, change_indexes):

            # We don't want to try and upload an empty comment.
            if issue.all_comments[0].body == "":
                comments_to_ignore.append(change_index)
                continue

            new_comment: Any = (
                self.service.get_repo(self.repo_name)
                .get_issue(issue.number)
                .create_comment(issue.all_comments[0].body[0])
            )

            current_issue: GitHubIssue = issues[change_index["issue"]]
            current_comment: GitHubIssueComment = current_issue.all_comments[
                change_index["comment"]
            ]
            current_comment.updated_at = convert_utc_timezone(
                new_comment.updated_at, self.options.timezone
            )

            change_count += 1

        buffered_info_message(
            self.nvim, f"Uploaded {change_count} comments to GitHub. "
        )

        return issues, comments_to_ignore

    def upload_issues(
        self, issues: List[GitHubIssue], tag: str
    ) -> Tuple[List[GitHubIssue], List[int]]:
        """upload_issues

        Upload issues with the specific tag to GitHub.
        """

        if self.service is None:
            self.nvim.err_write("Github service not currently running...\n")
            return [], []

        issues_to_upload, change_indexes = self.filter_issues(issues, tag)
        issues_to_ignore: List[int] = []
        change_count: int = 0

        for issue, index in zip(issues_to_upload, change_indexes):
            # We don't want to try and upload an empty issue/title.
            if issue.title == "" or issue.all_comments[0].body == "":
                issues_to_ignore.append(index)
                continue

            new_issue: Any = self.service.get_repo(self.repo_name).create_issue(
                title=issue.title,
                body=issue.all_comments[0].body[0],
                labels=issue.labels,
            )

            issues[index].number = new_issue.number
            issues[index].all_comments[0].updated_at = convert_utc_timezone(
                new_issue.updated_at, self.options.timezone
            )

            change_count += 1

        buffered_info_message(self.nvim, f"Uploaded {change_count} issues to GitHub. ")

        return issues, issues_to_ignore

    def update_comments(
        self, issues: List[GitHubIssue], tag: str
    ) -> Tuple[List[GitHubIssue], List[Dict[str, int]]]:
        """update_comments

        Update existing comments with the specific tag on GitHub.
        """

        if self.service is None:
            self.nvim.err_write("Github service not currently running...\n")
            return [], []

        comments_to_upload, change_indexes = self.filter_comments(issues, tag)
        comments_to_ignore: List[Dict[str, int]] = []
        update_count: int = 0

        for issue, change_index in zip(comments_to_upload, change_indexes):
            comment: GitHubIssueComment = issue.all_comments[0]

            # Comment 0 is actually the issue body, not a comment.
            if comment.number == 0:
                github_comment: Any = self.service.get_repo(self.repo_name).get_issue(
                    issue.number
                )

                github_edit_time: str = convert_utc_timezone(
                    github_comment.updated_at, self.options.timezone
                )

                if github_edit_time != comment.updated_at:
                    buffered_info_message(
                        self.nvim,
                        f"Mismatch with comment {issue.number}:{comment.number}.",
                    )
                    comments_to_ignore.append(change_index)
                    continue

                github_comment.edit(body=comment.body[0])

                # Grab the comment again, to sort the update time.
                github_comment = self.service.get_repo(self.repo_name).get_issue(
                    issue.number
                )
            else:

                github_comment = (
                    self.service.get_repo(self.repo_name)
                    .get_issue(issue.number)
                    .get_comments()[comment.number - 1]
                )

                github_edit_time = convert_utc_timezone(
                    github_comment.updated_at, self.options.timezone
                )

                if github_edit_time != comment.updated_at:
                    buffered_info_message(
                        self.nvim,
                        f"Mismatch with comment {issue.number}:{comment.number}. ",
                    )
                    comments_to_ignore.append(change_index)
                    continue

                github_comment.edit(comment.body[0])

                # Grab the comment again, to sort the update time.
                github_comment = (
                    self.service.get_repo(self.repo_name)
                    .get_issue(issue.number)
                    .get_comments()[comment.number - 1]
                )

            current_issue: GitHubIssue = issues[change_index["issue"]]
            current_comment: GitHubIssueComment = current_issue.all_comments[
                change_index["comment"]
            ]
            current_comment.updated_at = convert_utc_timezone(
                github_comment.updated_at, self.options.timezone
            )
            update_count += 1

        buffered_info_message(self.nvim, f"Updated {update_count} comments on GitHub. ")

        return issues, comments_to_ignore

    def update_issues(
        self, issues: List[GitHubIssue], tag: str
    ) -> Tuple[List[GitHubIssue], List[int]]:
        """update_issues

        Update existing issues with the specific tag on GitHub.
        """

        if self.service is None:
            self.nvim.err_write("Github service not currently running...\n")
            return [], []

        issues_to_upload, change_indexes = self.filter_issues(issues, tag)
        issues_to_ignore: List[int] = []
        update_count: int = 0

        for issue, change_index in zip(issues_to_upload, change_indexes):

            github_issue: Any = self.service.get_repo(self.repo_name).get_issue(
                issue.number
            )

            github_edit_time = convert_utc_timezone(
                github_issue.updated_at, self.options.timezone
            )

            if github_edit_time != issue.all_comments[0].updated_at:
                buffered_info_message(
                    self.nvim, f"Mismatch with issue {issue.number}. "
                )
                issues_to_ignore.append(change_index)
                continue

            github_issue.edit(
                title=issue.title,
                body=issue.all_comments[0].body[0],
                labels=issue.labels,
            )

            # Grab the issue again, to sort the update time.
            github_issue = self.service.get_repo(self.repo_name).get_issue(issue.number)
            current_issue: GitHubIssue = issues[change_index]
            issue_body_comment: GitHubIssueComment = current_issue.all_comments[0]
            issue_body_comment.updated_at = convert_utc_timezone(
                github_issue.updated_at, self.options.timezone
            )
            update_count += 1

        buffered_info_message(self.nvim, f"Updated {update_count} issues on GitHub. ")

        return issues, issues_to_ignore

    def complete_issues(self, issues: List[GitHubIssue]) -> None:
        """complete_issues

        Sort the complete status of the issues in the current buffer.
        We assume the buffer is always correct.
        """

        if self.service is None:
            self.nvim.err_write("Github service not currently running...\n")
            return

        change_counter: int = 0

        for issue in issues:
            github_issue: Any = self.service.get_repo(self.repo_name).get_issue(
                issue.number
            )

            if issue.complete and github_issue.state == "open":
                github_issue.edit(state="closed")
                change_counter += 1
            elif not issue.complete and github_issue.state == "closed":
                github_issue.edit(state="open")
                change_counter += 1

        buffered_info_message(
            self.nvim,
            f"Changed the completion status of {change_counter} issues on GitHub. ",
        )
