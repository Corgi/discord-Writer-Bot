#!/usr/bin/env python3
import lib
from pprint import pprint
from structures.xp import *

for x in range(300):
    xp = Experience(x)
    print(str(x) + ':' + str(xp.get_level()))
    print('Next level: ' + str(xp.get_next_level_xp()))