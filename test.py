#!/usr/bin/env python3
import lib
from pprint import pprint
from structures.singleton import *
from structures.db import *

config = lib.get('./settings.json')

db = Database.instance()
rows = db.get('test', {'id': 2}, ['id'])
pprint(rows)
