# Google Calendar Event Deduplicator

This repository contains some scripts that helped me deduplicate thousands of events that got created when I imported my calendar to Fastmail.

# ⚠️ Unmaintained ⚠️ 

## Requirements

The scripts have the same requirements as [described in the Google Calendar Quickstart example](https://developers.google.com/calendar/api/quickstart/python)
1. Python 2.6 or greater
2. The pip package management tool
3. A Google Cloud Platform project with the API enabled
4. Authorization credentials for a desktop application
5. A Google account with Google Calendar enabled

## Usage

1. Install the necessary libraries by running `pip install -r requirements.txt` in `src`
2. Generate an OAuth Client ID for a Desktop Application and save the file as `credentials.json` in the same path as the scripts
3. Run any of the scripts in `src`

## Caveats

Since this is a quick and dirty hack for myself there are some caveats:
- Duplicate events are simply matched by a prefix that Fastmail added to their events, replace it with the prefix that was added to your events
- There is a very annoying and [possibly undocumented](https://stackoverflow.com/questions/15473732/google-calendar-api-calendar-usage-limits-exceeded) rate limit on the number of requests you can fire in a - unknown to me - timespan, maybe due to the app being in Test-mode when I generated the OAuth credentials

## Disclaimer

I have no intention to maintain or troubleshoot this code: I published it because it helped me fix my problem and it might help someone else.

## Credits

The authentication parts of the code were mostly taken from Google's [quick-start example](https://github.com/googleworkspace/python-samples/blob/797d879e0a5d05d17f22608dd8c9d441019ea8e0/calendar/quickstart/quickstart.py#L35)
