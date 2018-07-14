"""nvim_github_class

The Github class, with Neovim options to log information
back to the user.
"""

import json
from os import path

from github import Github
from nvim_diary_template.helpers.file_helpers import check_cache


class SimpleNvimGithub():
    """SimpleNvimGithub

    A class to deal with the simple interactions with the Github API.
    """

    def __init__(self, nvim, options):
        self.nvim = nvim
        self.config_path = options.config_path
        self.options = options

        self.service = self.setup_github_api()

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

    def service_is_not_ready(self):
        """service_is_not_ready

        Check if the Github API service is ready.
        """
        if self.service is None:
            return True

        return False

    def get_all_open_issues(self):
        """get_all_open_issues

        Returns a list of all the open issues, which will include ones that
        are in the exclude list.
        """

        if self.service_is_not_ready():
            return []

        page_token = None
        calendar_list = self.service.calendarList() \
            .list(pageToken=page_token).execute()

        all_calendars = {}

        for calendar_list_entry in calendar_list['items']:
            all_calendars[calendar_list_entry['summary']] = \
                calendar_list_entry['id']

        return all_calendars
