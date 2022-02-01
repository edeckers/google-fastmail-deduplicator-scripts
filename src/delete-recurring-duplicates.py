#!/usr/bin/env python3

from datetime import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
# SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
SCOPES = ['https://www.googleapis.com/auth/calendar']


def _parse_date_time(date_time_str: str) -> datetime:
  return datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M:%S.%f%z")


def _filter_recurring_events(events):
  return list(filter(lambda event: ('recurrence' in event), events))


def _filter_event_by_creation_date(event, date: datetime):
  creation_time = _parse_date_time(event['created'])

  return creation_time.date() == date.date()


def _filter_events_by_creation_date(events, date: datetime):
  return list(filter(lambda event: _filter_event_by_creation_date(event, date), events))


def _event_to_string(event):
  event_id = event['id']

  original_start_time = event['start'].get(
      'dateTime', event['start'].get('date'))

  is_cancelled = event['status'] == 'cancelled'
  if is_cancelled:
    return f"start={original_start_time}, event_id={event_id}: CANCELLED"

  created = event['created']

  maybe_location = event['location'] if 'location' in event else None
  maybe_summary = event['summary'] if 'summary' in event else None

  description = maybe_summary or maybe_location

  return f"start={original_start_time}, created={created}, event_id={event_id}, description={description}"


def _delete_event(service, event_id):
  rq = service.events().delete(
      calendarId='primary',
      eventId=event_id,
      sendNotifications=False,
      sendUpdates='none')
  return rq.execute()


def _build_service():
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          'credentials.json', SCOPES)
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
      token.write(creds.to_json())

  service = build('calendar', 'v3', credentials=creds)

  return service


def _rec_get_calendar_events_for_page(service, start_date, page_token=None):
  events_result = service.events().list(calendarId='primary', timeMin=start_date,
                                        maxResults=2500, singleEvents=False,
                                        pageToken=page_token).execute()
  events = events_result.get('items', [])

  if 'nextPageToken' in events_result:
    return events + _rec_get_calendar_events_for_page(service, start_date, events_result['nextPageToken'])

  return events


def main():
  try:
    service = _build_service()

    start_date = '1900-01-01T00:00:00Z'

    events = _rec_get_calendar_events_for_page(service, start_date)

    recurring_events = _filter_recurring_events(events)
    filtered_events = _filter_events_by_creation_date(
        recurring_events, datetime.strptime('2022-01-31', '%Y-%m-%d'))

    if not filtered_events:
      print('No events found.')
      return

    i0 = 1
    cnt0 = len(filtered_events)

    print(f"Start recurring: {cnt0}")
    for event in filtered_events:
      _delete_event(service, event['id'])
      print(f"[{i0}/{cnt0}] {_event_to_string(event)}")

      i0 += 1

  except HttpError as error:
    print('An error occurred: %s' % error)


if __name__ == '__main__':
  main()
