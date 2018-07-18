"""nvim_github_class

The Github class, with Neovim options to log information
back to the user.
"""

import json
from os import path

from github import Github

from nvim_diary_template.helpers.file_helpers import check_cache
from nvim_diary_template.utils.constants import ISSUE_CACHE_DURATION


class SimpleNvimGithub():
    """SimpleNvimGithub

    A class to deal with the simple interactions with the Github API.
    """

    def __init__(self, nvim, options):
        self.nvim = nvim
        self.config_path = options.config_path
        self.repo_name = options.repo_name
        self.options = options

        self.service = self.setup_github_api()

        self.issues = check_cache(
            self.config_path,
            'open_issues',
            ISSUE_CACHE_DURATION,
            self.get_all_open_issues
        )

    def setup_github_api(self):
        """setup_github_api

            Sets up the initial Github service, which can then be used
            for future work.
        """

        try:
            with open(path.join(self.config_path, "github_credentials.json")) as json_file:
                store = json.load(json_file)

            access_token = store['access_token']
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

        if self.repo_name == '':
            return True

        return False

    def get_all_open_issues(self):
        """get_all_open_issues

        Returns a list of all the open issues, which will include ones that
        are in the exclude list.
        """

        if self.service_not_valid():
            self.nvim.err_write(
                "Github service not currently running...\n"
            )
            return []

        issues = self.service.get_repo(self.repo_name).get_issues(state='open')

        issue_list = []

        for issue in issues:
            issue_list.append({
                'number': issue.number,
                'title': issue.title,
                'body': issue.body
            })

        return issue_list

    def get_comments_for_issue(self, issue_number):
        """get_comments_for_issue

        Gets all the comments for a given issue.
        """

        issue = self.service.get_repo(self.repo_name).get_issue(issue_number)
        comments = issue.get_comments()

        comment_bodies = []

        for comment in comments:
            comment_bodies.append(comment.body)

        return comment_bodies

    def upload_new_issues(self, issues):
        """upload_new_issues

        Upload new issues to GitHub.
        """

        new_issues = [
            issue for issue in issues if 'new' in issue['metadata']
        ]

        for issue in new_issues:
            issue_title = issue['title']
            issue_body = issue['all_comments'][0]

            self.service.get_repo(self.repo_name) \
                        .create_issue(issue_title, body=issue_body)

    def upload_new_comments(self, issues):
        """upload_new_comments

        Upload new comments to GitHub.
        """

        with open("E:\\before.json", 'w') as json_test:
            json.dump(issues, json_test)

        new_comments = []

        for issue in issues:
            for comment in issue['all_comments']:
                if 'new' in comment['comment_tags']:
                    new_comments.append({
                        'issue_number': issue['number'],
                        'comment': '\r\n'.join(comment['comment_lines'])
                    })

        with open("E:\\after.json", 'w') as json_test:
            json.dump(new_comments, json_test)

        for comment in new_comments:
            issue_number = comment['issue_number']
            comment_body = comment['comment']

            self.service.get_repo(self.repo_name) \
                        .get_issue(issue_number) \
                        .create_comment(comment_body)
