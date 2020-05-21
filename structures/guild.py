import lib
from operator import itemgetter
from structures.db import Database
from structures.user import User
from pprint import pprint

class Guild:

    TOP_LIMIT = 10

    def __init__(self, guild):

        # Initialise the database instance
        self.__db = Database.instance()
        self._guild = guild

    def get_top_xp(self):
        """
        Get the top {self.TOP_LIMIT} users in a guild, ordered by their XP
        :return: array
        """

        # The users might no longer be in the guild, so we will get more than 10 and just stop once we get 10 which are still active
        results = self.__db.getall('user_xp', {'guild': self._guild.id})
        results = sorted(results, key=itemgetter('xp'), reverse=True)

        # Build an array of User objects
        users = []
        for user in results:
            # If the user still exists in the guild, and we haven't got 10 yet, add to the return array
            guild_member = self._guild.get_member( int(user['user']) )
            if guild_member is not None and len(users) < self.TOP_LIMIT:
                users.append( User(user['user'], user['guild'], guild_member.display_name) )

        return users


