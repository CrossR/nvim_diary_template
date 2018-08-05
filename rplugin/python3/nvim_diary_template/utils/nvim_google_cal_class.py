"""nvim_google_cal_class

The google calendar class, with Neovim options to log information
back to the user.
"""

from datetime import date, datetime, time
from os import path

from googleapiclient import discovery
from httplib2 import Http
from oauth2client import file

from nvim_diary_template.helpers.file_helpers import check_cache, set_cache
from nvim_diary_template.helpers.google_calendar_helpers import (convert_events,
                                                                 create_google_event,
                                                                 format_google_events)
from nvim_diary_template.utils.constants import (CALENDAR_CACHE_DURATION,
                                                 EVENT_CACHE_DURATION,
                                                 ISO_FORMAT)


class SimpleNvimGoogleCal():
    """SimpleNvimGoogleCal

    A class to deal with the simple interactions with the Google Cal API.
    """

    def __init__(self, nvim, options):
        self.nvim = nvim
        self.options = options

        self.service = self.setup_google_calendar_api()

        if self.service_is_not_ready():
            return

        self.all_calendars = check_cache(
            self.config_path,
            "calendars",
            CALENDAR_CACHE_DURATION,
            self.get_all_calendars
        )

        self.filter_list = options.calendar_filter_list
        self.filtered_calendars = self.filter_calendars()

        self._events = check_cache(
            self.config_path,
            'events',
            EVENT_CACHE_DURATION,
            self.get_events_for_today
        )

    @property
    def config_path(self):
        """config_path

        Get the Users' config path.
        """

        return self.options.config_path

    @property
    def active(self):
        """active

        Is the Gcal service active?
        """

        return not self.service_is_not_ready()

    @property
    def todays_events(self):
        """todays_events

        Return todays events from the cache.
        """

        return check_cache(
            self.config_path,
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
        credentials = store.get()

        if not credentials or credentials.invalid:
            self.nvim.err_write(
                "Credentials invalid, try re-generating or checking the path.\n"
            )
            return None

        service = discovery.build('calendar', 'v3', http=credentials.authorize(Http()))

        return service

    def service_is_not_ready(self):
        """service_is_not_ready

        Check if the Google API service is ready.
        """
        if self.service is None:
            self.nvim.err_write(
                "Google service not ready...\n"
            )
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

    def get_events_for_today(self):
        """get_events_for_today

        Gets all the events for today calendars.
        Events are brought in from 00:00 on the first day, to 23:59 on the
        last day.
        """

        if self.service_is_not_ready():
            return []

        date_today = date.today()
        time_min = datetime.combine(date_today, time.min).isoformat() + 'Z'
        time_max = datetime.combine(date_today, time.max).isoformat() + 'Z'

        page_token = None
        events_in_timeframe = []

        for _, calendar_id in self.filtered_calendars.items():
            events = self.service.events().list(
                calendarId=calendar_id,
                pageToken=page_token,
                timeMin=time_min,
                timeMax=time_max
            ).execute()

            events_in_timeframe.extend(events['items'])

        return format_google_events(events_in_timeframe)

    def upload_to_calendar(self, markdown_events):
        """upload_to_calendar

        Given a set of events that are missing from Google calendar, will upload
        them to the calendar that is specified in the users options.
        """

        if self.service_is_not_ready():
            return

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
        set_cache(self.config_path, updated_events, 'events')

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
