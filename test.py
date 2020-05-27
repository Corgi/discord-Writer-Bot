#!/usr/bin/env python3
import lib
from pprint import pprint
from structures.db import *
from datetime import datetime, timezone
import pytz

fmt = '%Y-%m-%d %H:%M:%S %Z%z'

utc = datetime.now(timezone.utc)
london = pytz.timezone('Europe/London')
phoenix = pytz.timezone('America/Phoenix')
anc = pytz.timezone('America/Anchorage')

print("UTC time     {}".format(utc.isoformat()))
print("London time   {}".format(datetime.now(london)))
print("Phoenix time {}".format(datetime.now(phoenix)))

print('London UTC Offset: ' + str(datetime.now(london).ctime()))
print('Phoenix UTC Offset: ' + str(datetime.now(phoenix).strftime('%H:%m')))
