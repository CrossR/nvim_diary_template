from datetime import timedelta

# Global plugin constants
FILE_TYPE = '.md'
FILE_TYPE_WILDCARD = '*.md'

# Google Calendar Constants
CACHE_EPOCH_REGEX = '([0-9])+'
CALENDAR_CACHE_DURATION = timedelta(days=31)
EVENT_CACHE_DURATION = timedelta(minutes=30)

# DateTime Formats
TIME_FORMAT = "%H:%M"
ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"

# Regex constants
DATETIME_REGEX = r"[0-9]{1,2}\/[0-9]{1,2}\/[0-9]{4} [0-9]{1,2}:[0-9]{1,2}"
TIME_REGEX = r"[0-9]{1,2}:[0-9]{1,2}"
EVENT_REGEX = r"(?<=: ).*$"

# Markdown Constants
SCHEDULE_HEADING = "# Schedule"
PADDING = "   "
EMPTY_TODO = "[ ]"
CHECKED_TODO = "[X]"
