import json
import time as t
import glob

from datetime import date, datetime, time

from apiclient.discovery import build
from os import path
from httplib2 import Http
from oauth2client import client, file, tools


CALENDAR_CACHE_DURATION = 31


class SimpleGoogleCal():

    def __init__(self, options):
        self.service = self.setup_google_calendar_api(options.credentials_path)
        self.filter_list = options.calendar_filter_list
        self.load_calendars()

    def setup_google_calendar_api(self, credentials_path):
        """setup_google_calendar_api

            Sets up the initial Google calendar service, which can then be used
            for future work.
        """

        store = file.Storage(path.join(credentials_path, 'credentials.json'))
        creds = store.get()

        if not creds or creds.invalid:
            self.nvim.err_write(
                "Credentials invalid, try re-generating or checking the path."
            )

        service = build('calendar', 'v3', http=creds.authorize(Http()))

        return service


    def filter_calendars(self):
        """filter_calendars

        Filters the calendars to only those the user cares about.
        """

        return [cal for cal in self.all_calendars if cal not in self.filter_list]

    def get_all_calendars(self):
        """get_all_calendars

        Returns a list of all the users calendars, which will include ones that
        are in the exclude list.
        """

        page_token = None
        calendar_list = self.service.calendarList().list(pageToken=page_token).execute()

        all_calendars = []

        for calendar_list_entry in calendar_list['items']:
            all_calendars.append({
                'name':calendar_list_entry['summary'],
                'id': calendar_list_entry['id']
            })

        return all_calendars

    def store_calendars(self):
        """store_calendars

        Store calendars to a cache file to skip API call.
        """
        cache_file_name = f"cache/nvim_notes_cache_{int(t.time())}.json"
        with open(cache_file_name, 'w') as cache_file:
            json.dump(self.all_calendars, cache_file)

    def load_calendars(self):
        """load_calendars

        When possible, load the calendars from the cache, but default
        to the API when needed.
        """
        cache_file_pattern = f"cache/nvim_notes_cache_*.json"

        try:
            cache_file_name = glob.glob(cache_file_pattern)[0]

            epoch = cache_file_name.split("_")[3] \
                                   .split(".")[0]

            cache_file_creation_date = datetime.fromtimestamp(int(epoch))
            today = datetime.today()
            difference = today - cache_file_creation_date

            if difference.days <= CALENDAR_CACHE_DURATION:
                with open(cache_file_name) as cache_file:
                    self.all_calendars = json.load(cache_file)
        except IndexError:
            self.all_calendars = self.get_all_calendars()
            self.store_calendars()
        else:
            self.filtered_calendars = self.filter_calendars()


    def get_events_for_timeframe(self,
                                 start_date=None,
                                 end_date=None):
        """get_events_for_timeframe

        Gets all the events for a given period, from the filtered users
        calendars. Both the start and end date must be provided, else it will
        default to getting for the current day only.

        Events are brought in from 00:00 on the first day, to 23:59 on the
        last day.
        """

        if not start_date or not end_date:
            date_today = date.today()
            timeMin = datetime.combine(date_today, time.min).isoformat() + 'Z'
            timeMax = datetime.combine(date_today, time.max).isoformat() + 'Z'
        else:
            timeMin = datetime.combine(start_date, time.min).isoformat() + 'Z'
            timeMax = datetime.combine(end_date, time.max).isoformat() + 'Z'

        page_token = None
        events_in_timeframe = []

        for calendar_id in [d['id'] for d in self.filtered_calendars]:
            events = self.service.events().list(
                calendarId=calendar_id,
                pageToken=page_token,
                timeMin=timeMin,
                timeMax=timeMax).execute()

            events_in_timeframe.extend(events['items'])

            page_token = events.get('nextPageToken')
            if not page_token:
                break

        return self.format_events(events_in_timeframe)


    def format_events(self, events_list):
        """format_events

        Formats a list of events down to the event name, and the
        start and end date of the event.
        """

        filtered_events = []

        for event in events_list:
            event_dict = {
                'event_name': event['summary'],
                'start_time': event['start'],
                'end_time': event['end']
            }

            filtered_events.append(event_dict)

        return filtered_events

    def compare_events(markdown_events):
        events_today = self.get_events_for_timeframe()

        missing_events = [
            event for event in markdown_events if event not in events_today
        ]

        for event_string in missing_events:
            self.service.event.quickAdd(
                calendarId=calendar_id,
                text=event_string
            )


def get_events_for_day(options):
    """get_events_for_day

    A wrapper function to call the functions required to get all events
    for the current day.
    """
    google_calendar = SimpleGoogleCal(options)
    todays_events = google_calendar.get_events_for_timeframe()

    return todays_events
