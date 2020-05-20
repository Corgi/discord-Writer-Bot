import lib
from structures.db import Database

class User:

    def __init__(self, id, guild):

        # Initialise the database instance
        self.__db = Database.instance()
        self._id = id
        self._guild = guild
        self._xp = None

    def get_xp(self):

        # If xp is None then we have't got the record yet, so try and get it.
        if self._xp is None:
            self.load_xp()

    def load_xp(self):
        print('loading xp for {} in guild {}'.format(self._id, self._guild))
        xp = self.__db.


