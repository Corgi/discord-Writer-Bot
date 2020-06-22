import discord, lib, time
from discord.ext import commands
from structures.db import Database
from structures.event import Event
from structures.project import Project
from structures.user import User
from structures.wrapper import CommandWrapper

from pprint import pprint

class EventCommand(commands.Cog, CommandWrapper):

    def __init__(self, bot):
        self.bot = bot
        self.__db = Database.instance()
        self._supported_commands = ['create', 'rename', 'desc', 'description', 'img', 'image', 'delete', 'schedule', 'start', 'end', 'time', 'left', 'update', 'me', 'top', 'leaderboard', 'info']
        self._arguments = [
            {
                'key': 'cmd',
                'prompt': 'event:argument:cmd',
                'required': True,
                'check': lambda content : content in self._supported_commands,
                'error': 'event:err:argument:cmd'
            }
        ]

    @commands.command(name="event")
    @commands.guild_only()
    async def event(self, context, cmd=None, *opts):
        """
        Work in progress. Do not use this command yet.
        """
        # Check the arguments were all supplied and get a dict list of them and their values, after any prompts
        args = await self.check_arguments(context, cmd=cmd)
        if not args:
            return

        # Overwrite the variables passed in, with the values from the prompt and convert to lowercase
        cmd = args['cmd'].lower()

        if cmd == 'create':
            return await self.run_create(context, opts)
        elif cmd == 'delete':
            return await self.run_delete(context)
        elif cmd == 'rename':
            return await self.run_rename(context, opts)
        elif cmd == 'desc' or cmd == 'description':
            return await self.run_set(context, 'description', opts)
        elif cmd == 'img' or cmd == 'image':
            return await self.run_set(context, 'image', opts)
        elif cmd == 'start':
            return await self.run_start(context)
        elif cmd == 'end':
            return await self.run_end(context)
        elif cmd == 'time' or cmd == 'left':
            return await self.run_time(context)
        elif cmd == 'update':
            return await self.run_update(context, opts)
        elif cmd == 'me':
            return await self.run_me(context)
        elif cmd == 'info':
            return await self.run_info(context)


        # schedule
        # top
        # view
        # scheduled tasks

    async def run_info(self, context):
        """
        Get the event information embedded message
        :param context:
        :return:
        """
        user = User(context.message.author.id, context.guild.id, context)
        event = Event.get_by_guild(user.get_guild())

        # Make sure the event is running
        if event is None or not event.is_running():
            return await context.send(user.get_mention() + ', ' + lib.get_string('event:err:noexists', user.get_guild()))

        # embed = discord.Embed(title=user.get_name(), color=event.get_colour())
        # embed.add_field(name=lib.get_string('profile:lvlxp', user.get_guild()), value=profile['lvlxp'], inline=True)

        # Send the message
        return await context.send(embed=embed)

    async def run_me(self, context):
        """
        Check your own word count for the event so far
        :param context:
        :return:
        """
        user = User(context.message.author.id, context.guild.id, context)
        event = Event.get_by_guild(user.get_guild())

        # Make sure the event is running
        if event is None or not event.is_running():
            return await context.send(user.get_mention() + ', ' + lib.get_string('event:err:noexists', user.get_guild()))

        words = event.get_wordcount(user.get_id())
        return await context.send(user.get_mention() + ', ' + lib.get_string('event:wordcount', user.get_guild()).format(event.get_title(), words))

    async def run_update(self, context, amount):
        """
        Update the user's word count on the event
        :param context:
        :param amount:
        :return:
        """
        user = User(context.message.author.id, context.guild.id, context)
        event = Event.get_by_guild(user.get_guild())

        amount = lib.is_number(amount[0])
        if amount is False or amount < 0:
            return await context.send(user.get_mention() + ', ' + lib.get_string('err:validamount', user.get_guild()))

        # Make sure the event is running
        if event is None or not event.is_running():
            return await context.send(user.get_mention() + ', ' + lib.get_string('event:err:noexists', user.get_guild()))

        event.update_wordcount(user.get_id(), amount)
        return await context.send(user.get_mention() + ', ' + lib.get_string('event:updated', user.get_guild()).format(event.get_title(), amount))

    async def run_time(self, context):
        """
        Check how much time is left in the event
        :param context:
        :return:
        """
        user = User(context.message.author.id, context.guild.id, context)
        event = Event.get_by_guild(user.get_guild())
        now = int(time.time())

        # Make sure the event exists
        if event is None or not event.is_valid():
            return await context.send(user.get_mention() + ', ' + lib.get_string('event:err:noexists', user.get_guild()))

        # Is the event scheduled to start, but has not yet started?
        if not event.is_running() and event.is_scheduled():
            left = lib.secs_to_mins(event.get_start_time() - now)
            return await context.send(user.get_mention() + ', ' + lib.get_string('event:timetostart', user.get_guild()).format(left['m'], left['s']))

        # If the event is not running and it is NOT scheduled, then we don't know what time it will start.
        elif not event.is_running():
            return await context.send(user.get_mention() + ', ' + lib.get_string('event:err:noexists', user.get_guild()))

        # At this point, the event must be running. If it is scheduled, then we can get the time left from the end time. Otherwise, we don't know.
        elif event.is_scheduled():
            left = lib.secs_to_mins(event.get_end_time() - now)
            return await context.send(user.get_mention() + ', ' + lib.get_string('event:timeleft', user.get_guild()).format(left['m'], left['s']))

        else:
            return await context.send(user.get_mention() + ', ' + lib.get_string('event:noendtime', user.get_guild()))


    async def run_end(self, context):
        """
        End the event now
        :param context:
        :return:
        """
        user = User(context.message.author.id, context.guild.id, context)

        # Do they have the permissions to rename an event?
        self.check_permissions(context)

        event = Event.get_by_guild(user.get_guild())
        if event is None or not event.is_running():
            return await context.send(user.get_mention() + ', ' + lib.get_string('event:err:noexists', user.get_guild()))

        event.set_context(context)
        return await event.end()

    async def run_start(self, context):
        """
        Start the event now
        :param context:
        :return:
        """
        user = User(context.message.author.id, context.guild.id, context)

        # Do they have the permissions to rename an event?
        self.check_permissions(context)

        event = Event.get_by_guild(user.get_guild())
        if event is None or event.is_running():
            return await context.send(user.get_mention() + ', ' + lib.get_string('event:err:cannotstart', user.get_guild()))

        event.set_context(context)
        return await event.start()

    async def run_set(self, context, type, opts):
        """
        Set the value of something for the event, such as description or image url
        :param context:
        :param type:
        :param opts:
        :return:
        """
        user = User(context.message.author.id, context.guild.id, context)

        # Do they have the permissions to rename an event?
        self.check_permissions(context)

        # Check if there is an event running
        event = Event.get_by_guild(user.get_guild())
        if event is None or not event.is_valid():
            return await context.send(user.get_mention() + ', ' + lib.get_string('event:err:noexists', user.get_guild()))

        value = " ".join(opts[0:])

        if type == 'description':
            event.set_description(value)
        elif type == 'image':
            if len(value) > 255:
                return await context.send(user.get_mention() + ', ' + lib.get_string('event:err:img', user.get_guild()))
            event.set_image(value)

        # Save the changes
        event.save()

        return await context.send(user.get_mention() + ', ' + lib.get_string('event:set', user.get_guild()).format(type, value))

    async def run_rename(self, context, opts):
        """
        Rename the event
        :param context:
        :param opts:
        :return:
        """
        user = User(context.message.author.id, context.guild.id, context)

        # Do they have the permissions to rename an event?
        self.check_permissions(context)

        # Check if there is an event running
        event = Event.get_by_guild(user.get_guild())
        if event is None or not event.is_valid():
            return await context.send(user.get_mention() + ', ' + lib.get_string('event:err:noexists', user.get_guild()))

        # Get the title out of the arguments
        title = " ".join(opts[0:])

        # Make sure they specified a title.
        if len(title) == 0 or len(title) > 255:
            return await context.send(user.get_mention() + ', ' + lib.get_string('event:err:rename:title', user.get_guild()))

        # Create the event
        event.set_title(title)
        event.save()
        return await context.send(user.get_mention() + ', ' + lib.get_string('event:renamed', user.get_guild()).format(title))

    async def run_delete(self, context):
        """
        Delete the event on this server
        :param context:
        :return:
        """
        user = User(context.message.author.id, context.guild.id, context)

        # Do they have the permissions to delete an event?
        self.check_permissions(context)

        # Check if there is an event running
        event = Event.get_by_guild(user.get_guild())
        if event is None or not event.is_valid():
            return await context.send(user.get_mention() + ', ' + lib.get_string('event:err:noexists', user.get_guild()))

        # Make a fake prompt to wait for confirmation.
        argument = {'prompt': lib.get_string('event:deletesure', user.get_guild()), 'check': lambda resp: resp.lower() in ('y', 'yes', 'n', 'no')}

        response = await self.prompt(context, argument, True)
        if not response:
            return

        response = response.content

        # If they confirm, then delete the event.
        if response.lower() in ('y', 'yes'):
            event.delete()
            output = lib.get_string('event:deleted', user.get_guild()).format(event.get_title())
        else:
            # Otherwise, just print 'OK'
            output = 'OK'

        await context.send(context.message.author.mention + ', ' + output)


    async def run_create(self, context, opts):
        """
        Create an event on the server
        :param context:
        :param opts:
        :return:
        """
        user = User(context.message.author.id, context.guild.id, context)

        # Do they have the permissions to create an event?
        self.check_permissions(context)

        # Get the title out of the arguments
        title = " ".join(opts[0:])

        # Check if there is already an event running
        event = Event.get_by_guild(user.get_guild())
        if event is not None:
            return await context.send(user.get_mention() + ', ' + lib.get_string('event:err:alreadyexists', user.get_guild()))

        # Make sure they specified a title.
        if len(title) == 0 or len(title) > 255:
            return await context.send(user.get_mention() + ', ' + lib.get_string('event:err:title', user.get_guild()))

        # Create the event
        Event.create(guild=user.get_guild(), channel=context.message.channel.id, title=title)
        return await context.send(user.get_mention() + ', ' + lib.get_string('event:created', user.get_guild()).format(title))

    def check_permissions(self, context):
        """
        Reusable method to check the user has the correct permissions, depending on what they are trying to do
        :param context:
        :return:
        """
        permissions = context.message.author.permissions_in(context.message.channel)
        if permissions.manage_messages is not True:
            raise commands.errors.MissingPermissions(['manage_messages'])

def setup(bot):
    bot.add_cog(EventCommand(bot))