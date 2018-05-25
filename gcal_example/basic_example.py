from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from datetime import datetime, time, date

# Setup the Calendar API
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('calendar', 'v3', http=creds.authorize(Http()))

# Get all calendars
page_token = None
calendar_list = service.calendarList().list(pageToken=page_token).execute()

all_calendars = []

for calendar_list_entry in calendar_list['items']:
    all_calendars.append({
        'name':calendar_list_entry['summary'],
        'id': calendar_list_entry['id']
    })

print(all_calendars)

# Get events today for each calendar

date_today = date.today()
timeMin = datetime.combine(date_today, time.min).isoformat() + 'Z'
timeMax = datetime.combine(date_today, time.max).isoformat() + 'Z'

todays_events = []

for calendar_id in [d['id'] for d in all_calendars]:
    events = service.events().list(
        calendarId=calendar_id,
        pageToken=page_token,
        timeMin=timeMin,
        timeMax=timeMax).execute()

    todays_events.append(events['items'])

    page_token = events.get('nextPageToken')
    if not page_token:
        break

print(todays_events)


