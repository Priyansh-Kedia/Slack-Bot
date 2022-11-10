import re

from datetime import date, datetime, timedelta
import os.path
from dateutil.tz import tz
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from quickstart import authenticate

from Constants import *

class User:
    def __init__(self, email, timeZone):
        self.email = email
        self.timeZone = timeZone

class MeetInfo:
    def __init__(self, summary, sender, users, start_date_utc, end_date_utc, timeZone):
        self.summary = summary
        self.sender = sender
        self.users = users
        self.start_date_utc = start_date_utc
        self.end_date_utc = end_date_utc
        self.timeZone = timeZone

def send_meet_invites(meet_info):
    creds = authenticate()
    service = build('calendar', 'v3', credentials=creds)

    attendees = []
    users = meet_info.users
    sender = meet_info.sender
    timeZone = meet_info.timeZone
    dateTime = meet_info.start_date_utc
    endTime = meet_info.end_date_utc
    
    for user in users:
        attendees.append({'email': user.email})

    print(meet_info.summary, dateTime, timeZone, endTime, attendees)

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

def get_today_date():
    today = date.today()
    date_in_format = today.strftime(date_format)

    return date_in_format

def format_date(date):
    formatted_date = ""

    is_numeric = date.isnumeric()

    if is_numeric:
        if len(date) == 6:
            formatted_date = "20{}-{}-{}".format(date[4:], date[2:4], date[0:2])
        elif len(date) == 8:
            formatted_date = "{}-{}-{}".format(date[4:], date[2:4], date[0:2])
        else:
            formatted_date = ""
    else:
        formatted_date = ""

    return formatted_date

def get_end_time(date, time, length_of_meet):
    end_time = datetime.strptime("{}T{}".format(date, time), date_time_format) + timedelta(hours = length_of_meet)
    end_time = end_time.strftime(date_time_format)
    return end_time

def format_time(time):
    is_numeric = time.isnumeric()

    formatted_time = ""

    if is_numeric:
        if len(time) == 4:
            formatted_time = "{}:{}:00".format(time[0:2], time[2:4])
        
    return formatted_time

def get_one_hour_after(n = 1):
    current_time = datetime.now()
    future_time = current_time + timedelta(hours = n)

    formatted_time = future_time.strftime(time_format)
    return formatted_time

def get_date_time_from_text(text):
    date_regex = r'd=(\w+)'
    time_regex = r't=(\w+)'

    dates = re.findall(date_regex, text)
    times = re.findall(time_regex, text)

    date = dates[0] if dates else get_today_date()
    date = format_date(date)
   
    time = times[0] if times else get_one_hour_after()
    time = format_time(time)

    return date, time

def get_length_from_text(text):
    length_regex = r'l=(\w+)'
    lengths = re.findall(length_regex, text)

    length = lengths[0] if lengths else 60 # (in mins)

    if not length.isnumeric():
        length = ""
    else:
        length = int(length) / float(60)

    return length

def get_time_zone_from_text(text):
    tz_regex = r'tz=(\w+)'
    timeZones = re.findall(tz_regex, text)

    # timeZone = timeZones[0] if timeZones else default timezone

    return timeZone

def get_time_in_utc(time_):
    local_tz = tz.tzlocal()
    utc_tz = ZoneInfo("UTC")
    time_ = datetime.strptime(time_, date_time_format)
    time_ = time_.replace(tzinfo = local_tz)
    time_utc = time_.astimezone(utc_tz)

    return time_utc.strftime(date_time_format)

def get_summary_from_text(text):
    summary_regex = 's="(.*?)"'
    summaries = re.search(summary_regex, text)

    summary = summaries.group(1) if summaries else "Meeting"
    print(summary)
    return summary

def create_meet_from_text(text, sender_id, client):
    users, sender = get_users_from_text(text, sender_id, client)

    date, time = get_date_time_from_text(text)
    # handle case of date or time to be empty

    length_of_meet = get_length_from_text(text)
    # Handle empty length

    end_time = get_end_time(date, time, length_of_meet)

    start_date_utc, end_date_utc = get_time_in_utc("{}T{}".format(date, time)), get_time_in_utc(end_time)
    timeZone = "Africa/Abidjan"
    summary = get_summary_from_text(text)
    meet_info = MeetInfo(summary, sender, users, start_date_utc, end_date_utc, timeZone)
    send_meet_invites(meet_info)

