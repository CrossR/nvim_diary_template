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

        return issues
