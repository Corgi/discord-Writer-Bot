import lib, time
from structures.db import Database
from structures.xp import Experience

class User:

    def __init__(self, id, guild, context=None, name=None):

        # Initialise the database instance
        self.__db = Database.instance()
        self.__context = context
        self._id = int(id)
        self._guild = int(guild)
        self._name = name
        self._xp = None
        self._stats = None
        self._settings = None
        self._records = None

    def get_id(self):
        return self._id

    def get_guild(self):
        return self._guild

    def get_name(self):
        return self._name

    def get_mention(self):
        return f'<@{self._id}>'

    def reset(self):
        """
        Reset the entire user's stats, records, xp, etc...
        :return:
        """
        self.__db.delete('user_challenges', {'user': self._id})
        self.__db.delete('user_goals', {'user': self._id})
        self.__db.delete('user_records', {'user': self._id})
        self.__db.delete('user_stats', {'user': self._id})
        self.__db.delete('user_xp', {'user': self._id})


    def get_xp(self):

        # If xp is None then we have't got the record yet, so try and get it.
        if self._xp is None:
            self.load_xp()

        return self._xp

    def load_xp(self):
        xp = self.__db.get('user_xp', {'user': self._id})
        if xp:
            experience = Experience(xp['xp'])
            self._xp = {'id': xp['id'], 'xp': xp['xp'], 'lvl': experience.get_level(), 'next': experience.get_next_level_xp()}

    def get_xp_bar(self):

        xp = self.get_xp()

        if xp is not None:
            return lib.get_string('xp:info', self._guild).format(xp['lvl'], xp['xp'], (xp['xp'] + xp['next']))
        else:
            return ''

    def add_xp(self, amount):

        user_xp = self.get_xp()
        if user_xp:
            amount += user_xp['xp']

        return self.update_xp(amount)

    async def update_xp(self, amount):

        user_xp = self.get_xp()

        # If they already have an XP record, update it
        if user_xp:
            current_level = user_xp['lvl']
            result = self.__db.update('user_xp', {'xp': amount}, {'id': user_xp['id']})
        else:
            # Otherwise, insert a new one
            current_level = 1
            result = self.__db.insert('user_xp', {'user': self._id, 'xp': amount})

        # Reload the XP onto the user object and into the user_xp variable
        self.load_xp()
        user_xp = self.get_xp()

        # If the level now is higher than it was, print the level up message
        if user_xp['lvl'] > current_level:
            await self.__context.send(lib.get_string('levelup', self._guild).format(self.get_mention(), user_xp['lvl']))

        return result

    def get_challenge(self):
        return self.__db.get('user_challenges', {'user': self._id, 'completed': 0})

    def set_challenge(self, challenge, xp):
        current_challenge = self.get_challenge()
        if not current_challenge:
            return self.__db.insert('user_challenges', {'user': self._id, 'challenge': challenge, 'xp': xp})
        else:
            return False

    def delete_challenge(self):
        return self.__db.delete('user_challenges', {'user': self._id})

    def complete_challenge(self, id):
        now = int(time.time())
        return self.__db.update('user_challenges', {'completed': now}, {'id': id})

    def get_stat(self, name):

        # If the stats property is None, then load it up first
        if self._stats is None:
            self.load_stats()

        # Now check if the key exists in the dictionary
        if name in self._stats:
            return self._stats[name]
        else:
            return None

    def load_stats(self):

        # Get the user_stats records
        records = self.__db.get_all('user_stats', {'user': self._id})

        # Reset the stats property
        self._stats = {}

        # Loop through the results and add to the stats property
        for row in records:
            self._stats[row['name']] = row['value']

    def update_stat(self, name, amount):

        # If the user already has a value for this stat, we want to update
        user_stat = self.get_stat(name)

        # Update the value in the array
        self._stats[name] = amount

        if user_stat:
            return self.__db.update('user_stats', {'value': amount}, {'user': self._id, 'name': name})

        # Otherwise, we want to insert a new one
        else:
            return self.__db.insert('user_stats', {'user': self._id, 'name': name, 'value': amount})

    def add_stat(self, name, amount):

        # If the user already has a value for this stat, we want to get their current amount so we can increment it
        user_stat = self.get_stat(name)

        if user_stat:
            amount = int(amount) + int(user_stat)

        # Now return the update_stat with the new amount (if incremented)
        return self.update_stat(name, amount)

    def get_settings(self):

        # If the settings property is None, then load it up first
        if self._settings is None:
            self.load_settings()

        return self._settings

    def get_setting(self, setting):

        # If the settings property is None, then load it up first
        if self._settings is None:
            self.load_settings()

        # Now check if the key exists in the dictionary
        if setting in self._settings:
            return self._settings[setting]
        else:
            return None

    def load_settings(self):

        # Get the user_settings records
        records = self.__db.get_all('user_settings', {'user': self._id})

        # Reset the stats property
        self._settings = {}

        # Loop through the results and add to the stats property
        for row in records:
            self._settings[row['setting']] = row['value']

    def update_setting(self, setting, value):

        # If the user already has a value for this setting, we want to update
        user_setting = self.get_setting(setting)

        # Update the value in the array
        self._settings[setting] = value

        if user_setting:
            return self.__db.update('user_settings', {'value': value}, {'user': self._id, 'setting': setting})

        # Otherwise, we want to insert a new one
        else:
            return self.__db.insert('user_settings', {'user': self._id, 'setting': setting, 'value': value})

    def get_record(self, name):

        # If the records property is None, then load it up first
        if self._records is None:
            self.load_records()

        # Now check if the key exists in the dictionary
        if name in self._records:
            return self._records[name]
        else:
            return None

    def load_records(self):

        # Get the user_settings records
        records = self.__db.get_all('user_records', {'user': self._id})

        # Reset the stats property
        self._records = {}

        # Loop through the results and add to the stats property
        for row in records:
            self._records[row['record']] = row['value']

    def update_record(self, name, value):

        # If the user already has a value for this record, we want to update
        user_record = self.get_record(name)

        # Update the value in the array
        self._records[name] = value

        if user_record:
            return self.__db.update('user_records', {'value': value}, {'user': self._id, 'record': name})

        # Otherwise, we want to insert a new one
        else:
            return self.__db.insert('user_records', {'user': self._id, 'record': name, 'value': value})

    def calculate_user_reset_time(self):
        timezone = self.get_setting('timezone') or 'UTC'
        return lib.get_midnight_utc(timezone)

    def get_goal(self, type):
        return self.__db.get('user_goals', {'user': self._id, 'type': type})

    def set_goal(self, type, value):

        user_goal = self.get_goal(type)
        if user_goal:
            return self.__db.update('user_goals', {'goal': value}, {'id': user_goal['id']})
        else:
            next_reset = self.calculate_user_reset_time()
            return self.__db.insert('user_goals', {'type': type, 'goal': value, 'user': self._id, 'current': 0, 'completed': 0, 'reset': next_reset})

    def delete_goal(self, type):
        return self.__db.delete('user_goals', {'user': self._id, 'type': type})