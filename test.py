#!/usr/bin/env python3
import lib
from pprint import pprint
from structures.db import *
from datetime import datetime, timezone, timedelta, time
import pytz

user_timezone = 'America/Phoenix'
ft = '%d-%m-%Y, %H:%M:%S'

def get_midnight_utc(timezone):

    tz = pytz.timezone(timezone)

    today = datetime.now(tz)
    tomorrow = today + timedelta(days=1)

    midnight = tz.localize( datetime.combine(tomorrow, time(0, 0, 0, 0)), is_dst=None )
    midnight_utc = midnight.astimezone(pytz.utc)

    return int(midnight_utc.timestamp())



for t in ['Europe/London', 'America/Phoenix', 'Asia/Srednekolymsk', 'UTC']:
    result = get_midnight_utc(t)
    print(t + ': ' + str(result))

