"""nvim_google_cal_class

The google calendar class, with Neovim options to log information
back to the user.
"""

from datetime import date, datetime, time
from os import path
from typing import Any, Dict, List, Optional, Union

from googleapiclient import discovery, errors
from httplib2 import Http, HttpLib2Error
from oauth2client import file
from pynvim import Nvim

from ..classes.calendar_event_class import CalendarEvent
from ..classes.plugin_options import PluginOptions
from ..helpers.file_helpers import cache_valid, check_cache, set_cache
from ..helpers.google_calendar_helpers import (
    convert_events,
    create_google_event,
    format_google_events,
    get_calendar_objects,
)
from ..utils.constants import CALENDAR_CACHE_DURATION, EVENT_CACHE_DURATION, ISO_FORMAT


class SimpleNvimGoogleCal:
    """SimpleNvimGoogleCal

    A class to deal with the simple interactions with the Google Cal API.
    """

    def __init__(
        self,
        nvim: Nvim,
        options: PluginOptions,
        service: Optional[discovery.Resource] = None,
    ) -> None:
        self.nvim: Nvim = nvim
        self.options: PluginOptions = options

        if service is not None:
            self.service: discovery.Resource = service
        else:
            self.service = self.setup_google_calendar_api()

        if self.service_is_not_ready():
            return

        self.all_calendars: Dict[str, str] = check_cache(
            self.config_path,
            "calendars",
            CALENDAR_CACHE_DURATION,
            self.get_all_calendars,
        )

        self.filtered_calendars: Dict[str, str] = self.filter_calendars()

        self.events: List[CalendarEvent] = []
        self.events_set: Optional[datetime] = None

    @property
    def config_path(self) -> str:
        """config_path

        Get the Users' config path.
        """

        return self.options.config_path

    @property
    def active_events(self) -> List[CalendarEvent]:
        """active_events

        Return the current events, assuming they are valid.
        If they are out of date, re-run the getting from cache.
        """

        # If the current events are fine, just use them, rather than reparsing
        # the json file again.
        if self.events_set is not None and cache_valid(
            self.events_set, EVENT_CACHE_DURATION
        ):
            return self.events

        active_events: Union[List[Dict[str, Any]], List[CalendarEvent]] = check_cache(
            self.config_path,
            "events",
            EVENT_CACHE_DURATION,
            lambda: self.get_events_for_date(date.today()),
        )

        self.events = get_calendar_objects(active_events)
        self.events_set = datetime.now()

        return self.events

    @property
    def active(self) -> bool:
        """active

        Is the Gcal service active?
        """

        return not self.service_is_not_ready()

    def setup_google_calendar_api(self) -> Optional[Any]:
        """setup_google_calendar_api

            Sets up the initial Google calendar service, which can then be used
            for future work.
        """

        store: file.Storage = file.Storage(
            path.join(self.config_path, "credentials.json")
        )
        credentials: Any = store.get()

        if not credentials or credentials.invalid:
            self.nvim.err_write(
                "Credentials invalid, try re-generating or checking the path.\n"
            )
            return None

        service: Any = discovery.build(
            "calendar", "v3", http=credentials.authorize(Http())
        )

        return service

    def service_is_not_ready(self) -> bool:
        """service_is_not_ready

        Check if the Google API service is ready.
        """
        if self.service is None:
            self.nvim.err_write("Google service not ready...\n")
            return True

        return False

    def filter_calendars(self) -> Dict[str, str]:
        """filter_calendars

        Filters the calendars to only those the user cares about.
        """

        return {
            cal_name: cal_id
            for cal_name, cal_id in self.all_calendars.items()
            if cal_name not in self.options.calendar_filter_list
        }

    def get_all_calendars(self) -> Union[List[str], Dict[str, str]]:
        """get_all_calendars

        Returns a list of all the users calendars, which will include ones that
        are in the exclude list.
        """

        if self.service_is_not_ready():
            return []

        page_token = None
        calendar_list = self.service.calendarList().list(pageToken=page_token).execute()

        all_calendars: Dict[str, str] = {}

        for calendar_list_entry in calendar_list["items"]:
            all_calendars[calendar_list_entry["summary"]] = calendar_list_entry["id"]

        return all_calendars

    def get_events_for_date(self, current_date: date) -> List[CalendarEvent]:
        """get_events_for_date

        Gets all the events for given days calendars.
        Events are brought in from 00:00 on the first day, to 23:59 on the
        last day.
        """

        if self.service_is_not_ready():
            return []

        time_min: str = datetime.combine(current_date, time.min).isoformat() + "Z"
        time_max: str = datetime.combine(current_date, time.max).isoformat() + "Z"

        page_token = None
        events_in_timeframe: List[Dict[str, Any]] = []

        for _, calendar_id in self.filtered_calendars.items():
            events = (
                self.service.events()
                .list(
                    calendarId=calendar_id,
                    pageToken=page_token,
                    timeMin=time_min,
                    timeMax=time_max,
                    singleEvents=True,
                )
                .execute()
            )

            events_in_timeframe.extend(events["items"])

        event_list: List[CalendarEvent] = format_google_events(
            events_in_timeframe, str(current_date)
        )

        # If we've gone through the trouble of getting the events for today, should store them.
        if current_date == date.today():
            self.events = event_list
            self.events_set = datetime.now()

        return event_list

    def upload_to_calendar(
        self, markdown_events: List[CalendarEvent], diary_date: date
    ) -> None:
        """upload_to_calendar

        Given a set of events that are missing from Google calendar, will upload
        them to the calendar that is specified in the users options.
        """

        if self.service_is_not_ready():
            return

        todays_events: List[CalendarEvent] = convert_events(self.events, ISO_FORMAT)

        missing_events: List[CalendarEvent] = [
            event for event in markdown_events if event not in todays_events
        ]

        for event in missing_events:

            target_calendar: str = self.get_calendar_id(event.calendar)

            gcal_event: Dict[str, str] = create_google_event(
                event, self.options.timezone
            )

            try:
                self.service.events().insert(
                    calendarId=target_calendar, body=gcal_event
                ).execute()
            except (errors.HttpError, HttpLib2Error):
                self.nvim.err_write("Error adding events to calendar. Quitting.\n")
                return

        # Now that the events have been updated, update the cache.
        updated_events: List[CalendarEvent] = self.get_events_for_date(diary_date)
        set_cache(self.config_path, updated_events, "events")

        self.nvim.out_write(f"Added {len(missing_events)} events to Google calendar.\n")

    def get_calendar_id(self, target_calendar: str = "") -> str:
        """get_calendar_id

        Gets the ID of a calendar from its name.
        """

        if target_calendar == "":
            target_calendar = self.options.google_cal_name

        if target_calendar == "primary":
            return "primary"

        try:
            return self.all_calendars[target_calendar]
        except KeyError:
            self.nvim.err_write(f"No calendar named {target_calendar} exists.\n")
            return ""
