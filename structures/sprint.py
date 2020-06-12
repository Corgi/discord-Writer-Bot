import lib, math, numpy, time
from operator import itemgetter
from structures.db import Database
from structures.xp import Experience
from structures.user import User

from pprint import pprint

class Sprint:

    DEFAULT_POST_DELAY = 2 # 2 minutes

    def __init__(self, guild_id):

        # Initialise the database instance
        self.__db = Database.instance()

        self.bot = None

        # Initialise the variables to match the database record
        self.id = None
        self.guild = guild_id
        self.channel = None
        self.start = None
        self.end = None
        self.end_reference = None
        self.length = None
        self.createdby = None
        self.created = None
        self.completed = None

        # Try and load the sprint on this server, if there is one running
        self.load()

    def exists(self):
        """
        Check if a sprint exists on this server
        :return:
        """
        return self.id is not None

    def load(self):
        """
        Try to load the sprint out of the database for the given guild_id
        :return: bool
        """
        result = self.__db.get('sprints', {'guild': self.guild, 'completed': 0})
        if result:
            self.id = result['id']
            self.guild = result['guild']
            self.channel = result['channel']
            self.start = result['start']
            self.end = result['end']
            self.end_reference = result['end_reference']
            self.length = result['length']
            self.createdby = result['createdby']
            self.created = result['created']
            self.completed = result['completed']
            return True
        else:
            return False

    def set_bot(self, bot):
        """
        Set the discord bot object into the sprint to be used for sending messages in the cron
        :param bot:
        :return:
        """
        self.bot = bot

    def is_finished(self):
        """
        Check if a sprint is finished based on the end time.
        This is different from checking if it is completed, which is based on the completed field
        :return: bool
        """
        now = int(time.time())
        return self.exists() and now > self.end

    def has_started(self):
        """
        Check if the sprint has started yet
        :return:
        """
        now = int(time.time())
        return self.start <= now

    def is_user_sprinting(self, user_id):
        """
        Check if a given user is in the sprint
        :param int user_id:
        :return:
        """
        user_ids = self.get_users()
        return user_id in user_ids

    def is_declaration_finished(self):
        """
        Check if everyone sprinting has declared their final word counts
        :return: bool
        """
        results = self.__db.get_all_sql('SELECT * FROM sprint_users WHERE sprint = %s AND ending_wc = 0', [self.id])
        return len(results) == 0

    def get_user_sprint(self, user_id):
        """
        Get a sprint_users record for the given user on this sprint
        :param user_id:
        :return:
        """
        return self.__db.get('sprint_users', {'sprint': self.id, 'user': user_id})

    def get_users(self):
        """
        Get an array of all the sprint_users records for users taking part in this sprint
        :return:
        """
        users = self.__db.get_all('sprint_users', {'sprint': self.id})
        return [int(row['user']) for row in users]

    def get_notify_users(self):
        """
        Get an array of all the users who want to be notified about new sprints on this server
        :return:
        """
        notify = self.__db.get_all('user_settings', {'guild': self.guild, 'setting': 'sprint_notify', 'value': 1})
        notify_ids = [int(row['user']) for row in notify]

        # We don't need to notify users who are already in the sprint, so we can exclude those
        users_ids = self.get_users()
        return numpy.setdiff1d(notify_ids, users_ids).tolist()

    def get_notifications(self, users):
        """
        Get an array of user mentions for each person in the supplied array of userids
        :return:
        """
        notify = []
        for user_id in users:
            usr = User(user_id, self.guild)
            notify.append(usr.get_mention())
        return notify

    def complete(self):
        """
        Mark this sprint as completed
        :return: void
        """
        now = int(time.time())
        self.__db.update('sprints', {'completed': now}, {'id': self.id})

    def join(self, user_id, starting_wc=0):
        """
        Add a user to a sprint with an optional starting word count number
        :param user_id:
        :param starting_wc:
        :return: void
        """

        # Get the current timestamp
        now = int(time.time())

        # If the sprint hasn't started yet, set the user's start time to the sprint start time, so calculations will work correctly.
        if not self.has_started():
           now = self.start

        # Insert the sprint_users record
        self.__db.insert('sprint_users', {'sprint': self.id, 'user': user_id, 'starting_wc': starting_wc, 'current_wc': starting_wc, 'ending_wc': 0, 'timejoined': now})

    def leave(self, user_id):
        """
        Remove a user from the sprint
        :param user_id:
        :return:
        """
        self.__db.delete('sprint_users', {'sprint': self.id, 'user': user_id})

    def cancel(self, context):
        """
        Cancel the sprint and notify the users who were taking part
        :return:
        """

        # Load current user
        user = User(context.message.author.id, context.guild.id, context)

        # Delete sprints and sprint_users records
        self.__db.delete('sprint_users', {'sprint': self.id})
        self.__db.delete('sprints', {'id': self.id})

        # If the user created this, decrement their created stat
        if user.get_id() == self.createdby:
            user.add_stat('sprints_started', -1)

    async def post_start(self, context=None):
        """
        Post the sprint start message
        :param: context This is passed through when posting start immediately. Otherwise if its in a cron job, it will be None and we will use the bot object.
        :return:
        """
        guild_id = context.guild.id if context is not None else self.guild

        # Build the message to display
        message = lib.get_string('sprint:started', guild_id).format(self.length)
        message += lib.get_string('sprint:joinednotifications', guild_id).format(', '.join( self.get_notifications(self.get_users()) ))

        # Add mentions for any user who wants to be notified
        notify = self.get_notify_users()
        if notify:
            message += lib.get_string('sprint:notifications', guild_id).format( ', '.join(self.get_notifications(notify)) )

        # If we passed the context through (ie. we are posting this message straight after the sprint start command) then we can use the context as normal
        if context is not None:
            return await context.send(message)

        # If not, it must be from the cron as they asked for a delay and we need to use the bot object
        else:
            # TODO
            pass


    async def post_delayed_start(self, context):
        """
        Post the message displaying when the sprint will start
        :return:
        """
        # Build the message to display
        now = int(time.time())
        delay = lib.secs_to_mins((self.start + 2) - now) # Add 2 seconds in case its slow to post the message. Then it will display the higher minute instead of lower.
        message = lib.get_string('sprint:scheduled', context.guild.id).format( delay['m'], self.length )

        # Add mentions for any user who wants to be notified
        notify = self.get_notify_users()
        if notify:
            message += lib.get_string('sprint:notifications', context.guild.id).format(', '.join(self.get_notifications(notify)))

        # Print the message to the channel
        return await context.send(message)

    def update_user(self, user_id, start=None, current=None, ending=None):

        update = {}

        if start is not None:
            update['starting_wc'] = start

        if current is not None:
            update['current_wc'] = current

        if ending is not None:
            update['ending_wc'] = ending

        # If the sprint hasn't started yet, set the user's start time to the sprint start time, so calculations will work correctly.
        if not self.has_started():
            update['timejoined'] = self.start

        self.__db.update('sprint_users', update, {'sprint': self.id, 'user': user_id})

    async def complete(self, context=None):
        """
        Finish the sprint, calculate all the WPM and XP and display results
        :return:
        """
        now = int(time.time())
        results = []

        # If the sprint has already completed, stop.
        if self.completed != 0:
            return

        # Mark this sprint as complete so the cron doesn't pick it up and start processing it again
        # self.__db.update('sprints', {'completed': now}, {'id': self.id})

        # Get all the users taking part
        users = self.get_users()

        # Loop through them and get their full sprint info
        for user_id in users:

            user = User(user_id, self.guild)
            user_sprint = self.get_user_sprint(user_id)

            # If they didn't submit an ending word count, use their current one
            if user_sprint['ending_wc'] == 0:
                user_sprint['ending_wc'] = user_sprint['current_wc']

            # Now we only process their result if they have declared something and it's different to their starting word count
            user_sprint['starting_wc'] = int(user_sprint['starting_wc'])
            user_sprint['current_wc'] = int(user_sprint['current_wc'])
            user_sprint['ending_wc'] = int(user_sprint['ending_wc'])
            user_sprint['timejoined'] = int(user_sprint['timejoined'])

            if user_sprint['ending_wc'] > 0 and user_sprint['ending_wc'] != user_sprint['starting_wc']:

                wordcount = user_sprint['ending_wc'] - user_sprint['starting_wc']
                time_sprinted = self.end_reference - user_sprint['timejoined']

                # If for some reason the timejoined or sprint.end_reference are 0, then use the defined sprint length instead
                if user_sprint['timejoined'] <= 0 or self.end_reference == 0:
                    time_sprinted = self.length

                # Calculate the WPM from their time sprinted
                wpm = Sprint.calculate_wpm(wordcount, time_sprinted)

                # See if it's a new record for the user
                user_record = user.get_record('wpm')
                wpm_record = True if user_record is None or wpm > int(user_record) else False

                # If it is a record, update their record in the database
                if wpm_record:
                    user.update_record('wpm', wpm)

                # Give them XP for finishing the sprint
                await user.add_xp(Experience.XP_COMPLETE_SPRINT)

                # Increment their stats
                user.add_stat('sprints_completed', 1)
                user.add_stat('sprints_words_written', wordcount)
                user.add_stat('total_words_written', wordcount)

                # Increment their words towards their goal
                await user.add_to_goals(wordcount)

                # TODO: Project

                # TODO: Event

                # Push user to results
                results.append({
                    'user': user,
                    'wordcount': wordcount,
                    'wpm': wpm,
                    'wpm_record': wpm_record,
                    'xp': Experience.XP_COMPLETE_SPRINT
                })

        # Sort the results
        results = sorted(results, key=itemgetter('wordcount'), reverse=True)

        # Now loop through them again and apply extra XP, depending on their position in the results
        position = 1

        for result in results:

            # If the user finished in the top 5 and they weren't the only one sprinting, earn extra XP
            if position <= 5 and len(results) > 1:

                extra_xp = math.ceil(Experience.XP_WIN_SPRINT / position)
                await result['user'].add_xp(extra_xp)

            # If they actually won the sprint, increase their stat by 1
            if position == 1:
                result['user'].add_stat('sprints_won', 1)

            position += 1

        # Post the final message with the results
        if len(results) > 0:

            position = 1
            message = lib.get_string('sprint:results:header', self.guild)
            for result in results:

                message = message + lib.get_string('sprint:results:row', self.guild).format(position, result['user'].get_mention(), result['wordcount'], result['wpm'], result['xp'])

                # If it's a new PB, append that string as well
                if result['wpm_record'] is True:
                    message = message + lib.get_string('sprint:results:pb', self.guild)

                position += 1

        else:
            message = lib.get_string('sprint:nowordcounts', self.guild)

        # Send the message, either via the context or directly to the channel
        await self.say(message, context)

    async def say(self, message, context=None):
        """
        Send a message to the channel, via context if supplied, or direct otherwise
        :param message:
        :param context:
        :return:
        """
        if context is not None:
            return await context.send(message)
        else:
            # TODO
            pass

    def calculate_wpm(amount, seconds):
        """
        Calculate words per minute, from words written and seconds
        :param amount:
        :param seconds:
        :return:
        """
        mins = seconds / 60
        return int(amount / mins)

    def create(guild, channel, start, end, end_reference, length, createdby, created):

        # Insert the record into the database
        db = Database.instance()
        db.insert('sprints', {'guild': guild, 'channel': channel, 'start': start, 'end': end, 'end_reference': end_reference, 'length': length, 'createdby': createdby, 'created': created})

        # Return the new object using this guild id
        return Sprint(guild)
