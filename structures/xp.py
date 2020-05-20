import sys, os, lib, pymysql, warnings

sys.path.append(os.path.abspath('../'))

class Experience:

    XP_COMPLETE_SPRINT = 25
    XP_WIN_SPRINT = 100
    XP_COMPLETE_GOAL = {
        "daily": 100
    }

