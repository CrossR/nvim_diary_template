"""file_helpers

Simple helpers to help with opening and finding files.
"""

import glob
import json
import re
import time as t
from datetime import datetime, timedelta
from os import makedirs, path, remove
from typing import Any, Callable, Dict, List, Match, Optional, Union

from ..classes.data_class_json import EnhancedJSONEncoder
from ..classes.plugin_options import PluginOptions
from ..utils.constants import CACHE_EPOCH_REGEX, DIARY_FOLDER


DictOrObjList = Union[List[Dict[Any, Any]], List[Any]]


def get_file_content(file_path: str) -> List[str]:
    """get_file_content

    Return the content of the passed note file.
    """

    with open(file_path) as note_file:
        return note_file.read().split("\n")


def get_diary_path(options: PluginOptions, note_name: str) -> str:
    """get_diary_path

    Gives a full path, given just a diary name.
    """
    pattern: str = path.join(options.notes_path, DIARY_FOLDER, note_name)

    return glob.glob(pattern)[0]


def check_cache(
    config_path: str,
    data_name: str,
    data_age: timedelta,
    fallback_function: Callable[[], List[Any]],
) -> DictOrObjList:
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
                data: DictOrObjList = json.load(cache_file)
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
