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
        self._id = guild.id
        self._members = [member.id for member in self._guild.members]

    def get_members_in_sql(self):
        return ', '.join(str(m) for m in self._members)

    def get_top_xp(self):
        """
        Get the top {self.TOP_LIMIT} users in a guild, ordered by their XP
        :return: array
        """

        # Build the SQL query using the IDs of the guild members
        sql = 'SELECT user FROM user_xp WHERE user IN (' + self.get_members_in_sql() + ') ORDER BY xp DESC LIMIT ' + str(self.TOP_LIMIT)
        self.__db.cursor.execute(sql)
        results = self.__db.cursor.fetchall()

        users = []
        for user in results:
            guild_member = self._guild.get_member( int(user['user']) )
            usr = User(user['user'], self._id, None, guild_member.display_name)
            users.append( usr )

        return users