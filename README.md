# Google Calendar Event Deduplicator

This repository contains some scripts that helped me deduplicate thousands of events that got created when I imported my calendar to Fastmail.

# ⚠️ Unmaintained ⚠️ 

## Usage

Generate an OAuth Client ID for a Desktop Application and save the file as `credentials.json` in the same path as the scripts.

## Caveats

Since this is a quick and dirty hack for myself there are some caveats:
- Duplicate events are simply matched by a prefix that Fastmail added to their events, replace it with the prefix that was added to your events
- There is a very annoying and possibly undocumented rate limit on the number of requests you can fire in a - unknown to me - timespan, maybe due to the app being in Test-mode when I generated the OAuth credentials

## Disclaimer

I have no intention to maintain or troubleshoot this code: I published it because it helped me fix my problem and it might help someone else.

