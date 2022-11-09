import re

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from quickstart import authenticate

class User:
    def __init__(self, email, timeZone):
        self.email = email
        self.timeZone = timeZone

class MeetInfo:
    def __init__(self, summary, sender, users, date, time, length_of_meet, timeZone):
        self.summary = summary
        self.sender = sender
        self.users = users
        self.date = date
        self.time = time
        self.length_of_meet = length_of_meet
        self.timeZone = timeZone

def send_meet_invites(meet_info):
    creds = authenticate()
    service = build('calendar', 'v3', credentials=creds)

    users = meet_info.users
    sender = meet_info.sender
    timeZone = meet_info.timeZone
    dateTime = meet_info.date # Add time so that it is in format of datetime like '2022-11-28T09:00:00-07:00'
    endTime = dateTime + length_of_meet # configure this

    for user in users:
        attendees.append({'email': user.email})

    event = {
        'summary': meet_info.summary,
        'start': {
            'dateTime': dateTime,
            'timeZone': timeZone
        },
        'end': {
            'dateTime': endTime,
            'timeZone': timeZone
        },
        'attendees': attendees,
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10}
            ]
        }
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))



def get_users_info(client, sender_id, user_ids):
    users = []
    sender = None
    try:
        for user_id in user_ids:
            user = client.users_info(user = user_id)['user']
            user_obj = User(user["profile"]["email"], user["tz"])
            users.append(user_obj)

            if user["id"] == sender_id:
                sender = user_obj

    except e as Exception:
        print("Get user info threw exception {}".format(e))
    print(users)
    # send_meet_invites(users, sender)

    return users, sender


def get_users_from_text(text, sender_id, client):
    at_regex = r'@(\w+)'
    user_ids = re.findall(at_regex, text)
    user_ids.append(sender_id)
    user_ids = list(set(user_ids))

    users, sender = get_users_info(client, sender_id, user_ids)

    return users, sender

def get_date_time_from_text(text):
    date_regex = r'd=(\w+)'
    time_regex = r't=(\w+)'

    dates = re.findall(date_regex, text)
    times = re.findall(time_regex, text)
    # date = dates[0] if dates else todays date
    
    # time = times[0] if times else time after on hour

    
    return date, time

def get_length_from_text(text):
    length_regex = r'l=(\w+)'
    lengths = re.findall(length_regex)

    # length = lengths[0] if lengths else 60 (in mins)

    return length

def get_time_zone_from_text(text):
    tz_regex = r'tz=(\w+)'
    timeZones = re.findall(tz_regex, text)

    # timeZone = timeZones[0] if timeZones else default timezone

    return timeZone

def get_summary_from_text(text):
    summary_regex = r's=(\w+)'
    summaries = re.findall(summary_regex, text)

    # summary = summaries[0] if timeZones else "Meeting"

    return summary

def create_meet_from_text(text, sender_id, client):
    users, sender = get_users_from_text(text, sender_id, client)
    date, time = get_date_time_from_text(text)
    length_of_meet = get_length_from_text(text)
    timeZone = get_time_zone_from_text(text)
    summary = get_summary_from_text(text)
    meet_info = MeetInfo(summary, sender, users, date, time, length_of_meet, timeZone)
    send_meet_invites(meet_info)

