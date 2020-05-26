import os
import json
from collections import namedtuple
from pprint import pprint
from os import path

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
    if path.exists(file):
        return get(file)
    else:
        return get('./assets/json/en/' + asset + '.json')


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