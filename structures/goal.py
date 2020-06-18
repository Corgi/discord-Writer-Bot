import lib, time
from structures.db import Database

class Goal:

    def __init__(self):
        self.__db = Database.instance()
        pass

    async def task_reset(self, bot):
        """
        The scheduled task to reset user goals at midnight
        :param bot:
        :return:
        """
        # Find all the user_goal records which are due a reset
        now = int(time.time())

        records = self.__db.get_all_sql('SELECT * FROM user_goals WHERE reset <= %s', [now])
        for record in records:
            next = record['reset'] + (60*60*24)
            lib.debug('Setting next goal reset time for ' + str(record['user']) + ' to: ' + str(next))
            self.__db.update('user_goals', {'completed': 0, 'current': 0, 'reset': next}, {'id': record['id']})

        return True

