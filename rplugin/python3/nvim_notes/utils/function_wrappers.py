import glob
import json
import re
import time as t
from datetime import datetime
from functools import wraps
from os import makedirs, path

CACHE_EPOCH_REGEX = '([0-9])+'


class SimpleCache(object):
    """SimpleCache

    A simple class to be used as a function decorator to check for valid
    cache files.
    If one is found, then it can be used, but otherwise the original function
    is called to generate the data and cache it.
    """

    def __init__(self, data_name, data_age):
        self.data_name = data_name
        self.data_age = data_age

    def __call__(self, function):
        def wrapped_function(*args):
            current_folder = path.dirname(path.realpath(__file__))
            pattern = f"{current_folder}/cache/" + \
                "nvim_notes_{self.data_name}_cache_*.json"

            try:
                cache_file_name = glob.glob(pattern)[0]

                epoch = re.search(CACHE_EPOCH_REGEX, cache_file_name)[0]

                cache_file_creation_date = datetime.fromtimestamp(int(epoch))
                today = datetime.today()
                difference = today - cache_file_creation_date

                if difference.days <= self.data_age:
                    with open(cache_file_name) as cache_file:
                        data = json.load(cache_file)
            except (IndexError, FileNotFoundError):
                data = function(self)
                self.set_cache(data)

            return data
        return wrapped_function


    def set_cache(self, data):

        current_folder = path.dirname(path.realpath(__file__))
        cache_file_name = f"{current_folder}/cache/" + \
            f"nvim_notes_{self.data_name}_cache_{int(t.time())}.json"

        makedirs(path.dirname(cache_file_name), exist_ok=True)

        with open(cache_file_name, 'w') as cache_file:
            json.dump(data, cache_file)


def check_service(function):
    """check_service

    A decorator to check the Google cal service exists
    """

    @wraps(function)
    def wrapper(self):
        if self.service is None:
            return
        function(self)
    return wrapper


# def check_cache(function, data_name, data_age):
#     """check_cache

#     """

#     @wraps(function)
#     def wrapper(self):
#         pattern = f"{self.config_path}/cache/nvim_notes_{data_name}_cache_*.json"

#         try:
#             cache_file_name = glob.glob(cache_file_pattern)[0]

#             epoch = re.search(CACHE_EPOCH_REGEX, cache_file_name)[0]

#             cache_file_creation_date = datetime.fromtimestamp(int(epoch))
#             today = datetime.today()
#             difference = today - cache_file_creation_date

#             if difference.days <= data_age:
#                 with open(cache_file_name) as cache_file:
#                     data = json.load(cache_file)
#         except (IndexError, FileNotFoundError):
#             data = function(self)
#             set_cache(data, data_name)

#         return data

#     return wrapper
