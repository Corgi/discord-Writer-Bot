import lib, numpy, time
from structures.db import Database
from structures.user import User

class Sprint:

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
        users = self.get_users()
        user_ids = [e['id'] for e in users]
        return user_id in user_ids

    def get_users(self):
        """
        Get an array of all the sprint_users records for users taking part in this sprint
        :return:
        """
        users = self.__db.get_all('sprint_users', {'sprint': self.id})
        return [row['user'] for row in users]

    def get_notify_users(self):
        """
        Get an array of all the users who want to be notified about new sprints on this server
        :return:
        """
        notify = self.__db.get_all('user_settings', {'guild': self.guild, 'setting': 'sprint_notify', 'value': 1})
        notify_ids = [row['user'] for row in notify]

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
        now = int(time.time())
        self.__db.insert('sprint_users', {'sprint': self.id, 'user': user_id, 'starting_wc': starting_wc, 'ending_wc': 0, 'timejoined': now})

    async def cancel(self, context):
        """
        Cancel the sprint and notify the users who were taking part
        :return:
        """

        # Get the users sprinting and create an array of mentions
        users = self.get_users()
        notify = self.get_notifications(users)

        # Load current user
        user = User(context.message.author.id, context.guild.id, context)

        # Delete sprints and sprint_users records
        self.__db.delete('sprint_users', {'sprint': self.id})
        self.__db.delete('sprints', {'id': self.id})

        # If the user created this, decrement their created stat
        if user.get_id() == self.createdby:
            user.add_stat('sprints_started', -1)

        message = lib.get_string('sprint:cancelled', user.get_guild())
        message = message + ', '.join(notify)
        return await context.send(message)

    async def post_start(self, context=None):
        """
        Post the sprint start message
        :param: context This is passed through when posting start immediately. Otherwise if its in a cron job, it will be None and we will use the bot object.
        :return:
        """
        guild_id = context.guild.id if context is not None else self.guild

        # Build the message to display
        message = lib.get_string('sprint:started', guild_id).format(self.length)
        message += ', '.join( self.get_notifications(self.get_users()) )

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

    def create(guild, channel, start, end, end_reference, length, createdby, created):

        # Insert the record into the database
        db = Database.instance()
        db.insert('sprints', {'guild': guild, 'channel': channel, 'start': start, 'end': end, 'end_reference': end_reference, 'length': length, 'createdby': createdby, 'created': created})

        # Return the new object using this guild id
        return Sprint(guild)