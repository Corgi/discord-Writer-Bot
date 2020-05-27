#!/usr/bin/env python3
import lib
from pprint import pprint
from structures.db import *

db = Database.instance()
db.insert('user_challenges', {'guild': 1, 'user': 2})