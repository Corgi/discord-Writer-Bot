import json, math, os, pytz, random, string
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

def get_supported_languages():
    """
    Get an array of supported language packs the guilds can choose from
    :return:
    """
    return ['en']

def is_supported_language(lang):
    """
    Check if we support the specified language pack
    :param lang:
    :return:
    """
    return lang in get_supported_languages()

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

def secs_to_days(seconds, format="{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"):
    """
    Convert a number of seconds, into days, hours, minutes and seconds
    E.g. 65 seconds -> 0 days, 1 minute 5 seconds
    :param seconds:
    :param format:
    :return: dict
    """
    tdelta = timedelta(seconds=seconds)
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return format.format(**d)

def is_valid_datetime(value, format):
    """
    Check if a value is valid date in the specified format
    :param value:
    :param format:
    :return:
    """
    try:
        date = datetime.strptime(value, format)
        return True
    except ValueError:
        return False

def find(list, key, value):
    """
    Find a dictionary element by one of its values in a list
    :param list:
    :param key:
    :param value:
    :return:
    """
    index = False

    for i, dic in enumerate(list):
        if dic[key] == value:
            index = i

    return list[index] if index is not False else False

def debug(txt):
    """
    Do something with a message for debugging purposes
    :param txt:
    :return:
    """
    time = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
    print('['+str(time)+'][DEBUG] ' + str(txt))

def generate_error_code():
    """
    Generate a 12 character error code to store in the error log, so they can be found more easily from reports.
    :return:
    """
    code = ''
    for x in range(3):
        code = code + ''.join(random.choice(string.ascii_uppercase) for i in range(3))
        if x < 2:
            code = code + '/'

    return code

def error(txt, use_code=None):
    """
    Do something with a message for debugging purposes
    :param txt:
    :return:
    """
    time = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
    code = generate_error_code() if use_code is None else use_code

    file = open('logs/error.log', 'a')
    file.write('['+str(time)+'][ERROR]['+code+'] ' + str(txt))
    file.close()
    return code
