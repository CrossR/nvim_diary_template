import glob
import json
import re
import time as t
from datetime import date, datetime, time
from os import makedirs, path, remove

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import client, file, tools

from nvim_notes.helpers.google_calendar_helpers import (convert_events,
                                                        create_google_event,
                                                        format_google_events)
from nvim_notes.utils.constants import (CACHE_EPOCH_REGEX,
                                        CALENDAR_CACHE_DURATION,
                                        EVENT_CACHE_DURATION, ISO_FORMAT)


class SimpleNvimGoogleCal():

    def __init__(self, nvim, options):
        self.nvim = nvim
        self.config_path = options.config_path
        self.options = options

        self.service = self.setup_google_calendar_api()
        self.all_calendars = self.check_cache(
            "calendars",
            CALENDAR_CACHE_DURATION,
            self.get_all_calendars
        )

        self.filter_list = options.calendar_filter_list
        self.filtered_calendars = self.filter_calendars()

        self.set_cache(self.filter_calendars, 'filtered')

        self._events = self.check_cache(
            'events',
            EVENT_CACHE_DURATION,
            self.get_events_for_today
        )

    @property
    def todays_events(self):
        return self.check_cache(
            "events",
            EVENT_CACHE_DURATION,
            self.get_events_for_today
        )

    def setup_google_calendar_api(self):
        """setup_google_calendar_api

            Sets up the initial Google calendar service, which can then be used
            for future work.
        """

        store = file.Storage(path.join(self.config_path, "credentials.json"))
        creds = store.get()

        if not creds or creds.invalid:
            self.nvim.err_write(
                "Credentials invalid, try re-generating or checking the path.\n"
            )
            return

        service = build('calendar', 'v3', http=creds.authorize(Http()))

        return service

    def service_is_not_up(self):
        if self.service is None:
            return True

        return False

    def filter_calendars(self):
        """filter_calendars

        Filters the calendars to only those the user cares about.
        """

        return {
            cal_name: cal_id for cal_name, cal_id in self.all_calendars.items()
            if cal_name not in self.filter_list
        }

    def get_all_calendars(self):
        """get_all_calendars

        Returns a list of all the users calendars, which will include ones that
        are in the exclude list.
        """

        if self.service_is_not_up():
            return

        page_token = None
        calendar_list = self.service.calendarList() \
            .list(pageToken=page_token).execute()

        all_calendars = {}

        for calendar_list_entry in calendar_list['items']:
            all_calendars[calendar_list_entry['summary']] = \
                calendar_list_entry['id']

        return all_calendars

    def get_events_for_today(self):
        """get_events_for_today

        Gets all the events for today calendars.
        Events are brought in from 00:00 on the first day, to 23:59 on the
        last day.
        """

        if self.service_is_not_up():
            return

        date_today = date.today()
        timeMin = datetime.combine(date_today, time.min).isoformat() + 'Z'
        timeMax = datetime.combine(date_today, time.max).isoformat() + 'Z'

        page_token = None
        events_in_timeframe = []

        for _, calendar_id in self.filtered_calendars.items():
            events = self.service.events().list(
                calendarId=calendar_id,
                pageToken=page_token,
                timeMin=timeMin,
                timeMax=timeMax
            ).execute()

            events_in_timeframe.extend(events['items'])

            page_token = events.get('nextPageToken')
            if not page_token:
                break

        return format_google_events(events_in_timeframe)

    def check_cache(self, data_name, data_age, fallback_function):
        """check_cache

        A function to check for valid cache files.
        If one is found, then it can be used, but otherwise the original function
        is called to generate the data and cache it.
        """

        pattern = f"{self.config_path}/cache/" + \
            f"nvim_notes_{data_name}_cache_*.json"

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
                self.set_cache(data, data_name)
        except (IndexError, FileNotFoundError):
            data = fallback_function()
            self.set_cache(data, data_name)

        return data

    def set_cache(self, data, data_name):
        """set_cache

        Given some data and a name, creates a cache file
        in the config folder. Cleans up any existing cache files
        when creting a new one.
        """

        cache_file_name = f"{self.config_path}/cache/" + \
            f"nvim_notes_{data_name}_cache_{int(t.time())}.json"

        pattern = f"{self.config_path}/cache/" + \
            f"nvim_notes_{data_name}_cache_*.json"

        makedirs(path.dirname(cache_file_name), exist_ok=True)
        old_cache_files = glob.glob(pattern)

        with open(cache_file_name, 'w') as cache_file:
            json.dump(data, cache_file)

        for old_cache_file in old_cache_files:
            remove(old_cache_file)

    def upload_to_calendar(self, markdown_events):
        """upload_to_calendar

        Given a set of events that are missing from Google calendar, will upload
        them to the calendar that is specified in the users options.
        """

        todays_events = convert_events(self.todays_events, ISO_FORMAT)

        missing_events = [
            event for event in markdown_events if event not in todays_events
        ]

        target_calendar = self.get_calendar_id()

        # TODO: This needs to be wrapped in an try/catch probably.
        for event in missing_events:
            gcal_event = create_google_event(event, self.options.timezone)

            self.service.events().insert(
                calendarId=target_calendar,
                body=gcal_event
            ).execute()

        # Now that the events have been updated, update the cache.
        updated_events = self.get_events_for_today()
        self.set_cache(updated_events, 'events')

        self.nvim.out_write(
            f"Added {len(missing_events)} events to {self.options.google_cal_name} calendar.\n"
        )

    def get_calendar_id(self):
        """get_calendar_id

        Gets the ID of a calendar from its name.
        """

        target_calendar = self.options.google_cal_name

        if target_calendar == 'primary':
            return 'primary'
        else:
            try:
                return self.all_calendars[target_calendar]
            except KeyError:
                self.nvim.err_write(
                    f"No calendar named {target_calendar} exists.\n"
                )
