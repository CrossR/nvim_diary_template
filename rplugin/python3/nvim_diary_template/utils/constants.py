"""constants

Constants to be used throughout the whole plugin.
"""

from datetime import timedelta

# Global plugin constants
FILE_TYPE_WILDCARD = '*.md'
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

TODO_REGEX = r"(?<=\[[ .oOX]\]: ).*$"
TODO_ONGOING_REGEX = r"(?<=    ).*$"
TODO_IS_CHECKED = r"\[X\]"
TODO_NOT_CHECKED = r"\[[ .oO]\]"

# TODO: Update both of these with metadata checks.
ISSUE_TITLE = r"^- \[[ X]\] "
ISSUE_COMMENT = r"- Comment \{[0-9]+\}:"

EVENT_REGEX = r"(?<=: ).*$"

HEADING_REGEX = r"# .*"

BULLET_POINT_REGEX = r"[ ]*?-"

# Markdown Constants
SCHEDULE_HEADING = "# Schedule"
ISSUE_HEADING = "# Issues"
PADDING = "    "
PADDING_SIZE = 4
EMPTY_TODO = "[ ]"
BULLET_POINT = "-"
