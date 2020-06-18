import json, math, os, pytz
from collections import namedtuple
from pprint import pprint
from os import path
from datetime import datetime, timezone, timedelta, time

def get(file,as_object=True):
    """
    Load a JSON file and return the contents as an object or array
    @param file: The path to the file to load
    @param as_object: Return as an object (can be accessed via object.property). Otherwise object['property'].
    @return object
    """

    with open(file, 'r') as data:
        if as_object:
            return json.load(data, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
        else:
            return json.load(data)

def get_lang(guild_id):
    """
    Check which language file the guild is using
    @param guild_id: The guild ID
    @return string: The language code
    """
    # TODO: Look up guild language in DB
    return 'en'

def get_string(str, guild_id):
    """
    Load a language string
    @param str: The language string code
    @param guild_id: The guild ID
    @return string: The full string in the correct language
    """

    lang = get_lang(guild_id)
    path = f'./data/lang/{lang}.json'
    strings = get(path, False)
    return strings[str] if str in strings else f'[[{str}]]'

def get_asset(asset, guild_id):
    """
    Load a JSON asset file, in the language of the guild_id
    :param asset:
    :param guild_id:
    :return:
    """

    file = './assets/json/' + get_lang(guild_id) + '/' + asset + '.json'

    # Try and get the file in the server's language first. If not, default to 'en'
    try:
        if path.exists(file):
            return get(file, False)
        else:
            return get('./assets/json/en/' + asset + '.json', False)
    except FileNotFoundError:
        return False


def find_in_array(lst, key, value):
    """
    Find a list element in an array.
    For example: `list = [{'id': 1, 'name': 'Test'}, {'id': 2, 'name': 'Test 2'}]`
    `find_in_array(list, 'name', 'Test')`
    Should return: `{'id': 1, 'name': 'Test'}`
    :param lst:
    :param key:
    :param value:
    :return:
    """
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return lst[i]
    return False

def is_number(value):
    """
    Check if a variable is a number (either int or can be converted to int). If it can be converted to int, it returns
    that number. Otherwise returns False.
    This also returns 1 for True, but it's good enough for now as it'll only be used for checking strings
    :param value:
    :return:
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return False

def get_midnight_utc(timezone):
    """
    Given a timezone name, get the UTC timestamp for midnight tomorrow.
    Used in things like goal resets, so that they reset at midnight in the user's timezone.

    :param timezone:
    :return:
    """

    tz = pytz.timezone(timezone)

    today = datetime.now(tz)
    tomorrow = today + timedelta(days=1)

    midnight = tz.localize( datetime.combine(tomorrow, time(0, 0, 0, 0)), is_dst=None )
    midnight_utc = midnight.astimezone(pytz.utc)

    return int(midnight_utc.timestamp())

def secs_to_mins(seconds):
    """
    Convert a number of seconds, into minutes and seconds
    E.g. 65 seconds -> 1 minute 5 seconds
    :param seconds:
    :return: dict
    """
    result = {'m': 0, 's': 0}

    if seconds < 60:
        result['s'] = seconds
    else:
        result['m'] = math.floor( seconds / 60 )
        result['s'] = math.ceil( seconds % 60 )

    return result

def debug(txt):
    """
    Do something with a message for debugging purposes
    :param txt:
    :return:
    """
    print('[DEBUG] ' + str(txt))