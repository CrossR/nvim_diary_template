"""nvim_github_class

The Github class, with Neovim options to log information
back to the user.
"""

import json
from os import path

from github import Github

from nvim_diary_template.classes.github_issue_class import (
    GitHubIssue,
    GitHubIssueComment,
)
from nvim_diary_template.helpers.file_helpers import check_cache
from nvim_diary_template.helpers.issue_helpers import (
    check_markdown_style,
    convert_utc_timezone,
)
from nvim_diary_template.helpers.neovim_helpers import buffered_info_message
from nvim_diary_template.utils.constants import (
    CALENDAR_CACHE_DURATION,
    ISSUE_CACHE_DURATION,
)


class SimpleNvimGithub:
    """SimpleNvimGithub

    A class to deal with the simple interactions with the Github API.
    """

    def __init__(self, nvim, options):
        self.nvim = nvim
        self.config_path = options.config_path
        self.repo_name = options.repo_name
        self.options = options

        self.service = self.setup_github_api()

        if self.service_not_valid():
            return

        self.issues = check_cache(
            self.config_path,
            "open_issues",
            ISSUE_CACHE_DURATION,
            self.get_all_open_issues,
        )

        self.repo_labels = check_cache(
            self.config_path,
            "repo_labels",
            CALENDAR_CACHE_DURATION,
            self.get_repo_issues,
        )

    @property
    def active(self):
        """active

        Is the Github service active?
        """
        return not self.service_not_valid()

    def setup_github_api(self):
        """setup_github_api

            Sets up the initial Github service, which can then be used
            for future work.
        """

        try:
            with open(
                path.join(self.config_path, "github_credentials.json")
            ) as json_file:
                store = json.load(json_file)

            access_token = store["access_token"]
        except (IOError, ValueError):
            self.nvim.err_write(
                "Credentials invalid, try re-generating or checking the path.\n"
            )
            return None

        service = Github(access_token)

        return service

    def service_not_valid(self):
        """service_not_valid

        Check if the Github API service is ready.
        """
        if self.service is None:
            return True

        if self.repo_name == "":
            return True

        return False

    def get_repo_issues(self):
        """get_repo_issues

        Get the labels for the current repo.
        """

        if self.service_not_valid():
            self.nvim.err_write("Github service not currently running...\n")
            return []

        # TODO: Add a wrapper for all GitHub calls.
        repo_labels = self.service.get_repo(self.repo_name).get_labels()

        return [label.name for label in repo_labels]

    def get_all_open_issues(self):
        """get_all_open_issues

        Returns a list of all the open issues, which will include ones that
        are in the exclude list.
        """

        if self.service_not_valid():
            self.nvim.err_write("Github service not currently running...\n")
            return []

        issues = self.service.get_repo(self.repo_name).get_issues(state="open")

        issue_list = []

        for issue in issues:

            initial_comment = GitHubIssueComment(
                number=0,
                body=issue.body,
                tags=[],
                updated_at=convert_utc_timezone(
                    issue.updated_at, self.options.timezone
                ),
            )
            issue_list.append(
                GitHubIssue(
                    number=issue.number,
                    complete=False,
                    title=issue.title,
                    all_comments=[initial_comment],
                    labels=[label.name for label in issue.labels],
                    metadata=[],
                )
            )

        return issue_list

    def get_comments_for_issue(self, issue_number):
        """get_comments_for_issue

        Gets all the comments for a given issue.
        """

        issue = self.service.get_repo(self.repo_name).get_issue(issue_number)
        comments = issue.get_comments()

        new_line = [""]
        comment_dicts = []

        # Add the issue body first
        comment_dicts.append(
            GitHubIssueComment(
                number=0,
                body=issue.body.splitlines() + new_line,
                tags=[],
                updated_at=convert_utc_timezone(
                    issue.updated_at, self.options.timezone
                ),
            )
        )

        for comment in comments:
            comment_dicts.append(
                GitHubIssueComment(
                    number=comment.number,
                    body=comment.body.splitlines() + new_line,
                    tags=[],
                    updated_at=convert_utc_timezone(
                        comment.updated_at, self.options.timezone
                    ),
                )
            )

        return comment_dicts

    @staticmethod
    def filter_comments(issues, tag):
        """filter_comments

        Filter comments for uploading, by a specific tag.
        """

        comments_to_upload = []
        change_indexes = []

        for issue_index, issue in enumerate(issues):
            for comment_index, comment in enumerate(issue.all_comments):
                if tag in comment.tags:
                    comment_lines = comment.body
                    processed_comment_lines = [
                        check_markdown_style(line, "github") for line in comment_lines
                    ]

                    comments_to_upload.append(
                        {
                            "issue_number": issue.number,
                            "comment_number": comment.number,
                            "comment": "\r\n".join(processed_comment_lines),
                        }
                    )

                    change_indexes.append(
                        {"issue": issue_index, "comment": comment_index}
                    )

        return comments_to_upload, change_indexes

    @staticmethod
    def filter_issues(issues, tag):
        """filter_issues

        Filter issues for uploading, by a specific tag.
        """

        issues_to_upload = []
        change_indexes = []

        for index, issue in enumerate(issues):
            if tag in issue.metadata:
                issue_body = issue.all_comments[0].body
                processed_body = [
                    check_markdown_style(line, "github") for line in issue_body
                ]

                issues_to_upload.append(
                    {
                        "number": issue.number,
                        "title": issue.title,
                        "labels": issue.labels,
                        "body": "\r\n".join(processed_body),
                    }
                )

                change_indexes.append(index)

        return issues_to_upload, change_indexes

    def upload_comments(self, issues, tag):
        """upload_comments

        Upload comments with the specific tag to GitHub.
        """

        comments_to_upload, change_indexes = self.filter_comments(issues, tag)

        for comment, change_index in zip(comments_to_upload, change_indexes):
            issue_number = comment["issue_number"]
            comment_body = comment["comment"]

            new_comment = (
                self.service.get_repo(self.repo_name)
                .get_issue(issue_number)
                .create_comment(comment_body)
            )

            current_issue = issues[change_index["issue"]]
            current_comment = current_issue["all_comments"][change_index["comment"]]
            current_comment["updated_at"] = convert_utc_timezone(
                new_comment.updated_at, self.options.timezone
            )

        buffered_info_message(
            self.nvim, f"Uploaded {len(comments_to_upload)} comments to GitHub. "
        )

        return issues

    def upload_issues(self, issues, tag):
        """upload_issues

        Upload issues with the specific tag to GitHub.
        """

        issues_to_upload, change_indexes = self.filter_issues(issues, tag)

        for issue, index in zip(issues_to_upload, change_indexes):
            issue_title = issue["title"]
            issue_body = issue["body"]
            issue_labels = issue["labels"]

            new_issue = self.service.get_repo(self.repo_name).create_issue(
                title=issue_title, body=issue_body, labels=issue_labels
            )

            issues[index]["number"] = new_issue.number
            issues[index]["all_comments"][0]["updated_at"] = convert_utc_timezone(
                new_issue.updated_at, self.options.timezone
            )

        buffered_info_message(
            self.nvim, f"Uploaded {len(issues_to_upload)} issues to GitHub. "
        )

        return issues

    def update_comments(self, issues, tag):
        """update_comments

        Update existing comments with the specific tag on GitHub.
        """

        comments_to_upload, change_indexes = self.filter_comments(issues, tag)

        for comment, change_index in zip(comments_to_upload, change_indexes):
            issue_number = comment["issue_number"]
            comment_number = comment["comment_number"]
            comment_body = comment["comment"]

            # Comment 0 is actually the issue body, not a comment.
            if comment_number == 0:
                self.service.get_repo(self.repo_name).get_issue(issue_number).edit(
                    body=comment_body
                )

                continue

            github_comment = (
                self.service.get_repo(self.repo_name)
                .get_issue(issue_number)
                .get_comments()[comment_number - 1]
            )

            github_comment.edit(comment_body)

            # Grab the comment again, to sort the update time.
            github_comment = (
                self.service.get_repo(self.repo_name)
                .get_issue(issue_number)
                .get_comments()[comment_number - 1]
            )

            current_issue = issues[change_index["issue"]]
            current_comment = current_issue["all_comments"][change_index["comment"]]
            current_comment["updated_at"] = convert_utc_timezone(
                github_comment.updated_at, self.options.timezone
            )

        buffered_info_message(
            self.nvim, f"Updated {len(comments_to_upload)} comments on GitHub. "
        )

        return issues

    def update_issues(self, issues, tag):
        """update_issues

        Update existing issues with the specific tag on GitHub.
        """

        issues_to_upload, change_indexes = self.filter_issues(issues, tag)

        for issue, change_index in zip(issues_to_upload, change_indexes):
            issue_number = issue["number"]
            issue_title = issue["title"]
            issue_body = issue["body"]
            issue_labels = issue["labels"]

            github_issue = self.service.get_repo(self.repo_name).get_issue(issue_number)

            github_issue.edit(title=issue_title, body=issue_body, labels=issue_labels)

            # Grab the issue again, to sort the update time.
            github_issue = self.service.get_repo(self.repo_name).get_issue(issue_number)
            current_issue = issues[change_index]
            issue_body_comment = current_issue["all_comments"][0]
            issue_body_comment["updated_at"] = convert_utc_timezone(
                github_issue.updated_at, self.options.timezone
            )

        buffered_info_message(
            self.nvim, f"Updated {len(issues_to_upload)} issues on GitHub. "
        )

        return issues

    def complete_issues(self, issues):
        """complete_issues

        Sort the complete status of the issues in the current buffer.
        We assume the buffer is always correct.
        """

        change_counter = 0

        for issue in issues:
            github_issue = self.service.get_repo(self.repo_name).get_issue(issue.number)

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
