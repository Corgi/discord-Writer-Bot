import lib, time
from structures.db import Database

class Event:

    def __init__(self, id):
        self.__db = Database.instance()
        self.__bot = None
        self.__context = None

        self.id = None
        self.guild = None
        self.channel = None
        self.title = None
        self.description = None
        self.img = None
        self.colour = 15105570 # Default colour to use if none specified
        self.startdate = None
        self.enddate = None
        self.started = None
        self.ended = None

        record = self.__db.get('events', {'id': id})
        if record:
            self.id = record['id']
            self.guild = record['guild']
            self.channel = record['channel']
            self.title = record['title']
            self.description = record['description']
            self.img = record['img']
            self.colour = record['colour']
            self.startdate = record['startdate']
            self.enddate = record['enddate']
            self.started = record['started']
            self.ended = record['ended']

    def is_valid(self):
        """
        Check if the event object is valid
        :return:
        """
        return self.id is not None

    def is_running(self):
        """
        Check if the event is currently running
        :return:
        """
        return self.is_valid() and self.get_started() > 0 and self.get_ended() == 0

    def is_scheduled(self):
        """
        Check if the event has a scheduled start time
        :return:
        """
        return self.get_start_time() > 0

    def get_id(self):
        """
        Get the event id
        :return:
        """
        return self.id

    def get_title(self):
        """
        Return the event title
        :return:
        """
        return self.title

    def get_start_time(self):
        """
        Get the scheduled start timestamp
        :return:
        """
        return int(self.startdate) if self.startdate is not None else 0

    def get_end_time(self):
        """
        Get the scheduled end timestamp
        :return:
        """
        return int(self.enddate) if self.enddate is not None else 0

    def get_started(self):
        """
        Get the started timestamp
        :return:
        """
        return int(self.started) if self.started is not None else 0

    def get_ended(self):
        """
        Get the ended timestamp
        :return:
        """
        return int(self.ended) if self.ended is not None else 0

    def get_guild(self):
        """
        Get the guild ID of the event
        :return:
        """
        return int(self.guild)

    def get_channel(self):
        """
        Get the channel ID of the event
        :return:
        """
        return int(self.channel)

    def get_colour(self):
        """
        Get the colour to use for the embedded messages for this event
        :return:
        """
        return self.colour

    def set_bot(self, bot):
        """
        Set the bot object into the event
        :param bot:
        :return:
        """
        self.__bot = bot
        return self

    def set_context(self, context):
        """
        Set the context into the event
        :param context:
        :return:
        """
        self.__context = context
        return self

    def set_title(self, title):
        """
        Set the title
        :param title:
        :return:
        """
        self.title = title
        return self

    def set_description(self, desc):
        """
        Set the description
        :param desc:
        :return:
        """
        self.description = desc
        return self

    def set_image(self, image):
        """
        Set the image URL
        :param image:
        :return:
        """
        self.img = image
        return self

    def set_colour(self, colour):
        """
        Set the colour to use
        :param colour:
        :return:
        """
        self.colour = colour
        return self

    def set_started(self, time):
        """
        Set the started time
        :param time:
        :return:
        """
        self.started = time
        return self

    def set_ended(self, time):
        """
        Set the ended time
        :param time:
        :return:
        """
        self.ended = time
        return self

    def delete(self):
        """
        Delete the event
        :return:
        """
        return self.__db.delete('events', {'id': self.id})

    def save(self):
        """
        Save the current state of the event
        :return:
        """
        return self.__db.update('events', {
            'title': self.title,
            'description': self.description,
            'img': self.img,
            'colour': self.colour,
            'startdate': self.startdate,
            'enddate': self.enddate,
            'started': self.started,
            'ended': self.ended
        }, {'id': self.id})

    async def start(self):
        """
        Start the event
        :return:
        """
        now = int(time.time())
        self.set_started(now)
        self.save()
        await self.say( lib.get_string('event:begin', self.get_guild()).format(self.get_title()) )

    async def end(self):
        """
        End the event
        :return:
        """
        now = int(time.time())
        self.set_ended(now)
        self.save()
        await self.say( lib.get_string('event:ended', self.get_guild()).format(self.get_title()) )

    def get_wordcount(self, user_id):
        """
        Get the word count for a user on the event
        :param user_id:
        :return:
        """
        record = self.__db.get('user_events', {'user': user_id, 'event': self.get_id()})
        if record:
            return record['words']
        else:
            return 0

    def update_wordcount(self, user_id, amount):
        """
        Update the event word count for a user
        :param user_id:
        :param amount:
        :return:
        """
        record = self.__db.get('user_events', {'user': user_id, 'event': self.get_id()})
        if record:
            return self.__db.update('user_events', {'words': amount}, {'id': record['id']})
        else:
            return self.__db.insert('user_events', {
                'event': self.get_id(),
                'user': user_id,
                'words': amount
            })

    async def say(self, message):
        """
        Send a message, either from the context or directly from the bot, depending on how it was called
        :param message:
        :return:
        """
        if self.__context is not None:
            return await self.__context.send(message)
        elif self.__bot is not None:
            channel = self.__bot.get_channel(self.get_channel())
            return await channel.send(message)

    @staticmethod
    def get_by_guild(guild_id, ended=0):
        """
        Get the event currently running on the specified guild
        :param guild_id:
        :return:
        """
        db = Database.instance()
        record = db.get('events', {'guild': guild_id, 'ended': ended})
        if record:
            return Event(record['id'])
        else:
            return None

    @staticmethod
    def create(guild, channel, title):
        """
        Create a new event
        :param guild:
        :param channel:
        :param title:
        :return:
        """
        db = Database.instance()
        return db.insert('events', {'guild': guild, 'channel': channel, 'title': title})