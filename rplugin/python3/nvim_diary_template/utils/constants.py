"""constants

Constants to be used throughout the whole plugin.
"""

from datetime import timedelta

# Global plugin constants
FILE_TYPE_WILDCARD = "*/diary/*.md"
DIARY_FOLDER = "diary"

# Google Calendar Constants
CACHE_EPOCH_REGEX = '([0-9])+'
CALENDAR_CACHE_DURATION = timedelta(days=31)
EVENT_CACHE_DURATION = timedelta(minutes=30)
ISSUE_CACHE_DURATION = timedelta(minutes=30)

# DateTime Formats
TIME_FORMAT = "%H:%M"
ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"

# Regex constants
DATETIME_REGEX = r"[0-9]{1,2}\/[0-9]{1,2}\/[0-9]{4} [0-9]{1,2}:[0-9]{1,2}"
TIME_REGEX = r"[0-9]{1,2}:[0-9]{1,2}"

# ToDo Existence and State Regex
TODO_REGEX = r"(?<=\[[ .oOX]\]: ).*$"
TODO_IS_CHECKED = r"\[X\]"
TODO_NOT_CHECKED = r"\[[ .oO]\]"

TODO_IN_PROGRESS_REGEX = r"\[[.oO]\]"
GITHUB_TODO = "[x]"
VIMWIKI_TODO = "[X]"

ISSUE_START = r"^## \[[ X]\] Issue \{[0-9]+\}:"
ISSUE_TITLE = r"^### Title: "
ISSUE_COMMENT = r"^### Comment \{[0-9]+\} - ([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}):"
ISSUE_METADATA = r"\+[a-zA-Z0-9]+"
ISSUE_LABELS = r"\+label:[a-zA-Z0-9]+"

EVENT_REGEX = r"(?<=: ).*$"

HEADING_REGEX = r"^# .*"

BULLET_POINT_REGEX = r"[ ]*?-"

# Markdown Constants
SCHEDULE_HEADING = "# Schedule"
ISSUE_HEADING = "# Issues"
HEADING_1 = "#"
HEADING_2 = "##"
HEADING_3 = "###"
PADDING = "    "
PADDING_SIZE = 4
EMPTY_TODO = "[ ]"
BULLET_POINT = "-"
