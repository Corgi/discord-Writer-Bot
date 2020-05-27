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

    def get_id(self):
        return self._id

    def get_guild(self):
        return self._guild

    def get_name(self):
        return self._name

    def get_mention(self):
        return f'<@{self._id}>'

    def get_xp(self):

        # If xp is None then we have't got the record yet, so try and get it.
        if self._xp is None:
            self.load_xp()

        return self._xp

    def load_xp(self):
        xp = self.__db.get('user_xp', {'user': self._id, 'guild' : self._guild})
        if xp:
            experience = Experience(xp['xp'])
            self._xp = {'id': xp['id'], 'xp': xp['xp'], 'lvl': experience.get_level(), 'next': experience.get_next_level_xp()}

    def get_xp_bar(self):

        xp = self.get_xp()

        if xp is not None:
            return lib.get_string('xp:info', self._guild).format(xp['lvl'], xp['xp'], (xp['xp'] + xp['next']))
        else:
            return ''

    async def add_xp(self, amount):

        user_xp = self.get_xp()

        # If they already have an XP record, update it
        if user_xp:
            current_level = user_xp['lvl']
            amount += user_xp['xp']
            result = self.__db.update('user_xp', {'xp': amount}, {'id': user_xp['id']})
        else:
            # Otherwise, insert a new one
            current_level = 1
            result = self.__db.insert('user_xp', {'user': self._id, 'guild': self._guild, 'xp': amount})

        # Reload the XP onto the user object and into the user_xp variable
        self.load_xp()
        user_xp = self.get_xp()

        # If the level now is higher than it was, print the level up message
        if user_xp['lvl'] > current_level:
            await self.__context.send( lib.get_string('levelup', self._guild).format(self.get_mention(), user_xp['lvl']) )

        return result

    def get_challenge(self):
        return self.__db.get('user_challenges', {'user': self._id, 'guild': self._guild, 'completed': 0})

    def set_challenge(self, challenge, xp):
        current_challenge = self.get_challenge()
        if not current_challenge:
            return self.__db.insert('user_challenges', {'user': self._id, 'guild': self._guild, 'challenge': challenge, 'xp': xp})
        else:
            return False

    def delete_challenge(self):
        return self.__db.delete('user_challenges', {'user': self._id, 'guild': self._guild})

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
        records = self.__db.get_all('user_stats', {'user': self._id, 'guild': self._guild})

        # Reset the stats property
        self._stats = {}

        # Loop through the results and add to the stats property
        for row in records:
            self._stats[row['name']] = row['value']

    def add_stat(self, name, amount):

        # If the user already has a value for this stat, we want to update
        user_stat = self.get_stat(name)

        if user_stat:
            amount += int(user_stat)
            return self.__db.update('user_stats', {'value': amount}, {'user': self._id, 'guild': self._guild, 'name': name})

        # Otherwise, we want to insert a new one
        else:
            return self.__db.insert('user_stats', {'user': self._id, 'guild': self._guild, 'name': name, 'value': amount})
