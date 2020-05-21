import lib
from structures.db import Database
from structures.xp import Experience

class User:

    def __init__(self, id, guild, name=None):

        # Initialise the database instance
        self.__db = Database.instance()
        self._id = int(id)
        self._guild = int(guild)
        self._name = name
        self._xp = None

    def get_name(self):
        return self._name

    def get_xp(self):

        # If xp is None then we have't got the record yet, so try and get it.
        if self._xp is None:
            self.load_xp()

        return self._xp

    def load_xp(self):
        xp = self.__db.get('user_xp', {'guild' : self._guild, 'user': self._id})
        if xp:
            experience = Experience(xp['xp'])
            self._xp = {'xp': xp['xp'], 'lvl': experience.get_level(), 'next': experience.get_next_level_xp()}

    def get_xp_bar(self):

        xp = self.get_xp()

        if xp is not None:
            return lib.get_string('xp:info', self._guild).format(xp['lvl'], xp['xp'], (xp['xp'] + xp['next']))
        else:
            return ''


