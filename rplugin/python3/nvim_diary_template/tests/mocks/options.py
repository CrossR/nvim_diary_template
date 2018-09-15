from typing import List


class MockPluginOptions:
    def __init__(self) -> None:

        self.active: bool = True
        self.notes_path: str = "notes"
        self.config_path: str = "config"
        self.daily_headings: List[str] = ["Notes"]
        self.auto_generate_diary_index = False
        self.use_google_calendar: bool = True
        self.calendar_filter_list: List[str] = []
        self.add_to_google_cal: bool = False
        self.google_cal_name: str = "primary"
        self.timezone: str = "Europe/London"
        self.use_github_repo: bool = True
        self.repo_name: str = ""
        self.user_name: str = ""
        self.sort_issues_on_upload: bool = False
