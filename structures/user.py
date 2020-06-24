import lib, math, time
from structures.db import Database
from structures.project import Project
from structures.xp import Experience

class User:

    def __init__(self, id, guild, context=None, name=None, bot=None, channel=None):

        # Initialise the database instance
        self.__db = Database.instance()
        self.__context = context
        self.__bot = bot
        self.__channel = channel
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
        """
        Try and get the user's name on the guild, or just return it if it was passed through.
        :return:
        """

        # If the name is empty but we have the context, we can get it from the guild member list
        if self._name is None and self.__context is not None and self.__context.guild is not None:
            guild_member = self.__context.guild.get_member( self._id )
            if guild_member is not None:
                self._name = guild_member.display_name

        # If the name is empty but we have the bot object, we can get it from the guilds and then the guild member list
        elif self._name is None and self.__bot is not None and self._guild is not None:
            guild_member = self.__bot.get_guild(self._guild).get_member(self._id)
            if guild_member is not None:
                self._name = guild_member.display_name

        return self._name

    def get_mention(self):
        return f'<@{self._id}>'

    def is_owner(self):
        """
        Check if this user is the bot owner
        :return:
        """
        return self.__bot is not None and self.__bot.app_info.owner.id == self._id

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
            return None

    def add_xp(self, amount):

        user_xp = self.get_xp()
        if user_xp:
            amount += int(user_xp['xp'])

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
            await self.say(lib.get_string('levelup', self._guild).format(self.get_mention(), user_xp['lvl']))

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

    def get_guild_setting(self, setting):
        """
        Get a user setting on a specific guild.
        This is mostly just used for things like sprint notifications. It's not settings they can manually set with the !myset command
        This is used more rarely, so we won't bother loading the settings into an array, we'll just go fetch it
        :param int setting:
        :return:
        """
        return self.__db.get('user_settings', {'user': self._id, 'setting': setting, 'guild': self._guild})

    def set_guild_setting(self, setting, value):
        """
        Set a user's setting for a specific guild
        :param str setting:
        :param str value:
        :return: Result of update or insert query
        """
        result = self.get_guild_setting(setting)
        if result:
            return self.__db.update('user_settings', {'value': value}, {'id': result['id']})
        else:
            return self.__db.insert('user_settings', {'user': self._id, 'guild': self._guild, 'setting': setting, 'value': value})

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
        """
        Get the user_goal record for this user and type
        :param type:
        :return:
        """
        return self.__db.get('user_goals', {'user': self._id, 'type': type})

    def get_goal_progress(self, type):
        """
        Get the user's goal progress
        :param type:
        :return:
        """
        progress = {
            'percent': 0,
            'done': 0,
            'left': 0,
            'goal': 0,
            'current': 0,
            'str': ''
        }

        user_goal = self.get_goal(type)
        if user_goal is not None:

            percent = math.floor((user_goal['current'] / user_goal['goal']) * 100)
            progress['done'] = math.floor(percent / 10)
            progress['left'] = 10 - progress['done']

            progress['percent'] = percent
            progress['goal'] = user_goal['goal']
            progress['current'] = user_goal['current']
            progress['str'] = '[' + ('-' * progress['done']) + ('  ' * progress['left']) + ']'

        # Can't be more than 10 or less than 0
        if progress['done'] > 10:
            progress['done'] = 10

        if progress['left'] < 0:
            progress['left'] = 0

        return progress

    def set_goal(self, type, value):

        user_goal = self.get_goal(type)
        if user_goal:
            return self.__db.update('user_goals', {'goal': value}, {'id': user_goal['id']})
        else:
            next_reset = self.calculate_user_reset_time()
            return self.__db.insert('user_goals', {'type': type, 'goal': value, 'user': self._id, 'current': 0, 'completed': 0, 'reset': next_reset})

    def delete_goal(self, type):
        return self.__db.delete('user_goals', {'user': self._id, 'type': type})

    async def add_to_goals(self, amount):
        """
        Add word written to all goals the user is running
        :param amount:
        :return:
        """
        for goal in ['daily']:
            await self.add_to_goal(goal, amount)

    async def add_to_goal(self, type, amount):

        user_goal = self.get_goal(type)
        if user_goal:

            value = int(amount) + int(user_goal['current'])
            if value < 0:
                value = 0

            # Is the goal completed now?
            already_completed = user_goal['completed']
            completed = user_goal['completed']
            if value >= user_goal['goal'] and not already_completed:
                completed = 1

            self.__db.update('user_goals', {'current': value, 'completed': completed}, {'id': user_goal['id']})

            # If we just met the goal, increment the XP and print out a message
            if completed and not already_completed:

                # Increment stat of goals completed
                self.add_stat(type + '_goals_completed', 1)

                # Increment XP
                await self.add_xp(Experience.XP_COMPLETE_GOAL[type])

                # Print message
                await self.say(lib.get_string('goal:met', self._guild).format(self.get_mention(), type, str(user_goal['goal']), str(Experience.XP_COMPLETE_GOAL[type])))


    def get_project(self, shortname):
        """
        Try and retrieve a project for this user, with the given shortname
        :param shortname:
        :return:
        """
        return Project.get(self._id, shortname)

    def get_projects(self):
        """
        Get all of the user's projects
        :return:
        """
        return Project.all(self._id)


    def create_project(self, shortname, title):
        """
        Create a new project
        :param shortname:
        :param title:
        :return:
        """
        return Project.create(self._id, shortname, title)

    async def say(self, message):
        """
        Send a message to the channel, via context if supplied, or direct otherwise
        :param message:
        :param context:
        :return:
        """
        if self.__context is not None:
            return await self.__context.send(message)
        elif self.__bot is not None:
            channel = self.__bot.get_channel(int(self.__channel))
            return await channel.send(message)