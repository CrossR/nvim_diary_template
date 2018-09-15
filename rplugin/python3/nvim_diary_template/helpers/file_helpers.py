"""file_helpers

Simple helpers to help with opening and finding files.
"""

import glob
import json
import re
import time as t
from datetime import datetime, timedelta
from os import makedirs, path, remove
from typing import Any, Callable, List, Union

from dateutil import parser

from ..classes.data_class_json import EnhancedJSONEncoder
from ..classes.plugin_options import PluginOptions
from ..utils.constants import (
    BULLET_POINT,
    CACHE_EPOCH_REGEX,
    DATE_FORMAT,
    DIARY_FOLDER,
    DIARY_INDEX_FILE,
    HEADING_2,
    HEADING_3,
)


def check_cache(
    config_path: str,
    data_name: str,
    data_age: timedelta,
    fallback_function: Callable[[], Any],
) -> Any:
    """check_cache

    A function to check for valid cache files.
    If one is found, then it can be used, but otherwise the original function
    is called to generate the data and cache it.
    """

    cache_path: str = path.join(config_path, "cache")
    makedirs(cache_path, exist_ok=True)

    pattern: str = path.join(
        cache_path, f"nvim_diary_template_{data_name}_cache_*.json"
    )

    try:
        cache_file_name: str = glob.glob(pattern)[0]

        epoch_search: Union[str, Any] = re.search(CACHE_EPOCH_REGEX, cache_file_name)
        epoch: str = epoch_search[0] if epoch_search is not None else ""

        cache_file_creation_date: datetime = datetime.fromtimestamp(int(epoch))
        today: datetime = datetime.today()
        difference: timedelta = today - cache_file_creation_date

        if difference <= data_age:
            with open(cache_file_name) as cache_file:
                data: Any = json.load(cache_file)
        else:
            data = fallback_function()
            set_cache(config_path, data, data_name)
    except (IndexError, FileNotFoundError):
        data = fallback_function()
        set_cache(config_path, data, data_name)

    return data


def set_cache(config_path: str, data: List[Any], data_name: str) -> None:
    """set_cache

    Given some data and a name, creates a cache file
    in the config folder. Cleans up any existing cache files
    when creating a new one.
    """

    cache_file_name: str = path.join(
        config_path,
        "cache",
        f"nvim_diary_template_{data_name}_cache_{int(t.time())}.json",
    )

    pattern: str = path.join(
        config_path, "cache", f"nvim_diary_template_{data_name}_cache_*.json"
    )

    makedirs(path.dirname(cache_file_name), exist_ok=True)
    old_cache_files: List[str] = glob.glob(pattern)

    with open(cache_file_name, "w") as cache_file:
        json.dump(data, cache_file, cls=EnhancedJSONEncoder)

    for old_cache_file in old_cache_files:
        remove(old_cache_file)


def generate_diary_index(options: PluginOptions) -> None:
    """generate_diary_index

    A helper function to generate the diary index page.
    This is currently needed as VimWiki will not make this file
    in the background.
    """

    diary_index_file = path.join(options.notes_path, DIARY_FOLDER, DIARY_INDEX_FILE)

    diary_files: List[str] = glob.glob(path.join(options.notes_path, "diary", "*.md"))
    diary_files = [path.split(diary)[-1].split(".")[0] for diary in diary_files]

    date_time_diaries: List[datetime] = [
        parser.parse(diary) for diary in diary_files if diary != "diary"
    ]
    sorted_diary_list: List[datetime] = sorted(
        date_time_diaries, key=lambda d: (d.year, d.month, d.day), reverse=True
    )

    full_markdown: List[str] = ["# Diary Index", ""]
    last_added_year: str = ""
    last_added_month: str = ""

    for diary in sorted_diary_list:

        current_month: str = diary.strftime("%B")
        current_year: str = diary.strftime("%Y")

        if current_year != last_added_year:
            full_markdown.append(f"{HEADING_2} {current_year}")
            last_added_year = current_year

        if current_month != last_added_month:
            full_markdown.extend(("", f"{HEADING_3} {current_month}", ""))
            last_added_month = current_month

        date = diary.strftime(DATE_FORMAT)
        full_markdown.append(f"{BULLET_POINT} [Diary for {date}]({date}.md)")

    with open(diary_index_file, "w") as diary_index:
        diary_index.write("\n".join(full_markdown))
