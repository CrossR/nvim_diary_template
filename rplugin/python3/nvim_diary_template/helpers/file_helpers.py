"""file_helpers

Simple helpers to help with opening and finding files.
"""

import glob
import json
import re
import time as t
from datetime import datetime
from os import makedirs, path, remove

from nvim_diary_template.utils.constants import CACHE_EPOCH_REGEX, DIARY_FOLDER


def get_file_content(file_path):
    """get_file_content

    Return the content of the passed note file.
    """

    with open(file_path) as note_file:
        return note_file.read().split("\n")


def get_diary_path(options, note_name):
    """get_diary_path

    Gives a full path, given just a diary name.
    """
    pattern = path.join(options.notes_path, DIARY_FOLDER, note_name)

    return glob.glob(pattern)[0]


def check_cache(config_path, data_name, data_age, fallback_function):
    """check_cache

    A function to check for valid cache files.
    If one is found, then it can be used, but otherwise the original function
    is called to generate the data and cache it.
    """

    cache_path = path.join(config_path, "cache")
    makedirs(cache_path, exist_ok=True)

    pattern = path.join(cache_path, f"nvim_diary_template_{data_name}_cache_*.json")

    try:
        cache_file_name = glob.glob(pattern)[0]

        epoch = re.search(CACHE_EPOCH_REGEX, cache_file_name)[0]

        cache_file_creation_date = datetime.fromtimestamp(int(epoch))
        today = datetime.today()
        difference = today - cache_file_creation_date

        if difference <= data_age:
            with open(cache_file_name) as cache_file:
                data = json.load(cache_file)
        else:
            data = fallback_function()
            set_cache(config_path, data, data_name)
    except (IndexError, FileNotFoundError):
        data = fallback_function()
        set_cache(config_path, data, data_name)

    return data


def set_cache(config_path, data, data_name):
    """set_cache

    Given some data and a name, creates a cache file
    in the config folder. Cleans up any existing cache files
    when creating a new one.
    """

    cache_file_name = path.join(
        config_path,
        "cache",
        f"nvim_diary_template_{data_name}_cache_{int(t.time())}.json",
    )

    pattern = path.join(
        config_path, "cache", f"nvim_diary_template_{data_name}_cache_*.json"
    )

    makedirs(path.dirname(cache_file_name), exist_ok=True)
    old_cache_files = glob.glob(pattern)

    with open(cache_file_name, "w") as cache_file:
        json.dump(data, cache_file)

    for old_cache_file in old_cache_files:
        remove(old_cache_file)
