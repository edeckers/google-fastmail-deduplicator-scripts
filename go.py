#!/usr/bin/env python3

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
# SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
SCOPES = ['https://www.googleapis.com/auth/calendar']


def _filter_events_with_attendees(events):
  return list(filter(lambda event: len(event['attendees'] if 'attendees' in event else []) > 0, events))


def _filter_non_recurring_events(events):
  return list(filter(lambda event: not 'recurringEventId' in event, events))

def _filter_recurring_events(events):
  return list(filter(lambda event: 'recurringEventId' in event, events))


def _filter_duplicate_events(events):
  return list(filter(lambda event: event['id'].startswith('1854280e-'), events))


def _delete_event(service, event_id):
  rq = service.events().delete(
      calendarId='primary',
      eventId=event_id,
      sendNotifications=False,
      sendUpdates='none')
  return rq.execute()


def _event_to_string(event):
  attendees = event['attendees'] if 'attendees' in event else "none"

  created = event['created']
  event_id = event['id']
  start = event['start'].get('dateTime', event['start'].get('date'))

  maybe_location = event['location'] if 'location' in event else None
  maybe_summary = event['summary'] if 'summary' in event else None

  description = maybe_summary or maybe_location
  # if not description:
  #   print (event)
  #   exit (0)

  return f"start={start}, created={created}, event_id={event_id}, description={description}"


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
                                        maxResults=50000, singleEvents=True,
                                        pageToken=page_token,
                                        orderBy='startTime').execute()
  events = events_result.get('items', [])

  if 'nextPageToken' in events_result:
    return events + _rec_get_calendar_events_for_page(service, start_date, events_result['nextPageToken'])

  return events


def main():
  try:
    service = _build_service()

    # Call the Calendar API
    start_date = '2015-01-01T00:00:00Z'

    events = _rec_get_calendar_events_for_page(service, start_date)

    if not events:
      print('No events found.')
      return

    # for event in events:
    #   print (event)

    # filtered_events = _filter_events_with_attendees(events)
    # filtered_events = _filter_non_recurring_events(events)
    duplicate_events = _filter_duplicate_events(events)
    duplicate_recurring_events = _filter_recurring_events(duplicate_events)
    duplicate_non_recurring_events = _filter_non_recurring_events(duplicate_events)

    i0 = 1
    cnt0 = len(duplicate_recurring_events)

    print (f"Start recurring: {cnt0}")
    for event in duplicate_recurring_events:
      id = event['recurringEventId']
      _delete_event(service, id)
      print(f"[{i0}/{cnt0}] {_event_to_string(event)}")

      i0 += 1

    i1 = 1
    cnt1 = len(duplicate_non_recurring_events)
    print (f"Start non-recurring: {cnt1}")
    for event in duplicate_non_recurring_events:
      id = event['id']
      _delete_event(service, id)
      print(f"[{i1}/{cnt1}] {_event_to_string(event)}")

      i1 += 1

  except HttpError as error:
    print('An error occurred: %s' % error)


if __name__ == '__main__':
  main()
