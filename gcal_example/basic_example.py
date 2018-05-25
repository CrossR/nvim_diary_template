from datetime import date, datetime, time

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import client, file, tools

FILTER_LIST = []
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'

def setup_google_calendar_api():
    """setup_google_calendar_api

        Sets up the initial Google calendar service, which can then be used
        for future work.
    """

    store = file.Storage('credentials.json')
    creds = store.get()

    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)

    service = build('calendar', 'v3', http=creds.authorize(Http()))

    return service


def filter_user_calendars(calender_list):
    """filter_user_calendars

    Given a list of all calendars, will remove the ones that events should
    be ignored from.
    """

    # TODO: Plumb through an actual filter list.
    return [cal for cal in calender_list if cal not in FILTER_LIST]

def get_user_calendars(service):
    """get_user_calendars

    Returns a list of user calendars, that has been filtered to only include
    those the user cares about.
    """

    page_token = None
    calendar_list = service.calendarList().list(pageToken=page_token).execute()

    all_calendars = []

    for calendar_list_entry in calendar_list['items']:
        all_calendars.append({
            'name':calendar_list_entry['summary'],
            'id': calendar_list_entry['id']
        })

    filtered_user_calendars = filter_user_calendars(all_calendars)

    return filtered_user_calendars


def get_events_for_timeframe(service,
                             calendar_list,
                             start_date = None,
                             end_date = None):
    """get_events_for_timeframe

    Gets all the events for a given period, for the calendars provided.
    Both the start and end date must be provided, else it will default to
    getting for the current day only.

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

    for calendar_id in [d['id'] for d in calendar_list]:
        events = service.events().list(
            calendarId=calendar_id,
            pageToken=page_token,
            timeMin=timeMin,
            timeMax=timeMax).execute()

        events_in_timeframe.extend(events['items'])

        page_token = events.get('nextPageToken')
        if not page_token:
            break

    return format_events(events_in_timeframe)


def format_events(events_list):
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


def run_test():
    calendar_service = setup_google_calendar_api()
    user_calendars = get_user_calendars(calendar_service)
    todays_events = get_events_for_timeframe(calendar_service, user_calendars)
    print(todays_events)


if __name__ == '__main__':
    run_test()