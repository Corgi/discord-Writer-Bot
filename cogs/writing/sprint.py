import discord, lib, time
from discord.ext import commands
from structures.generator import NameGenerator
from structures.sprint import Sprint
from structures.user import User
from structures.wrapper import CommandWrapper

class SprintCommand(commands.Cog, CommandWrapper):

    DEFAULT_LENGTH = 20 # 20 minutes
    DEFAULT_DELAY = 2 # 2 minutes
    DEFAULT_POST_DELAY = 2 # 2 minutes
    MAX_LENGTH = 60 # 1 hour
    MAX_DELAY = 60 * 24 # 24 hours

    def __init__(self, bot):
        self.bot = bot
        self._supported_commands = ['start', 'for', 'time', 'cancel', 'end', 'join', 'leave', 'users', 'wc', 'help', 'pb', 'notify', 'forget', 'project', 'status']
        self._arguments = [
            {
                'key': 'cmd',
                'prompt': 'sprint:argument:cmd',
                'required': True,
                'check': lambda content : content in self._supported_commands,
                'error': 'sprint:err:cmd'
            },
            {
                'key': 'opt1',
                'required': False,
            },
            {
                'key': 'opt2',
                'required': False,
            },
            {
                'key': 'opt3',
                'required': False,
            }
        ]

    @commands.command(name="sprint")
    async def sprint(self, context, cmd=None, opt1=None, opt2=None, opt3=None):
        """
        Write with your friends and see who can write the most in the time limit!
        When choosing a length and start delay, there are maximums of 60 minutes length of sprint, and 24 hours delay until sprint begins.
        NOTE: The bot checks for sprint changes every 15 seconds, so your start/end times might be off by +-15 seconds or so.

        Run `!help sprint` for more extra information, including any custom server settings related to sprints.

        Examples:
            !sprint start - Quickstart a sprint with the default settings,
            !sprint for 20 in 3 - Schedules a sprint for 20 minutes, to start in 3 minutes,
            !sprint for 20 at :30 - Schedules a sprint for 20 minutes, starting the next time it is half past the current hour (UTC),
            !sprint cancel - Cancels the current sprint. This can only be done by the person who created the sprint, or any users with the MANAGE_MESSAGES permission,
            !sprint join - Joins the current sprint,
            !sprint join 100 - Joins the current sprint, with a starting word count of 100,
            !sprint join 100 sword - Joins the current sprint, with a starting word count of 100 and sets your sprint to count towards your Project with the shortname "sword" (See: Projects for more info),
            !sprint leave - Leaves the current sprint,
            !sprint project sword - Sets your sprint to count towards your Project with the shortname "sword" (See: Projects for more info),
            !sprint wc 250 - Declares your final word count at 250,
            !sprint time - Displays the time left in the current sprint,
            !sprint users - Displays a list of the users taking part in the current sprint,
            !sprint pb - Displays your personal best wpm from sprints on this server. Run sprint pb reset to reset your personal best to 0 on the current server,
            !sprint notify - You will be notified when someone starts a new sprint,
            !sprint forget - You will no longer be notified when someone starts a new sprint,
            !sprint status - Shows you your current word count on the sprint,
            !sprint help - Displays a similar help screen to this one, with a few added bits of info
        """
        user = User(context.message.author.id, context.guild.id, context)

        # Check the arguments are valid
        args = await self.check_arguments(context, cmd=cmd, opt1=opt1, opt2=opt2, opt3=opt3)
        if not args:
            return

        # Convert cmd to lowercase
        cmd = args['cmd'].lower()

        # Start a sprint
        if cmd == 'start':
            return await self.run_start(context)
        elif cmd == 'for':

            length = opt1

            # If the second option is invalid, display an error message
            if opt2 is None or opt2.lower() not in ['now', 'in']:
                return await context.send(user.get_mention() + ', ' + lib.get_string('sprint:err:for:unknown', user.get_guild()))

            if opt2.lower() == 'now':
                delay = 0
            elif opt2.lower() == 'in':
                delay = opt3

            return await self.run_start(context, length, delay)

        elif cmd == 'cancel':
            return await self.run_cancel(context)

        elif cmd == 'notify':
            return await self.run_notify(context)

        elif cmd == 'forget':
            return await self.run_forget(context)

        elif cmd == 'time':
            return await self.run_time(context)

        elif cmd == 'join':
            return await self.run_join(opt1, opt2)


    async def run_join(self, starting_wc=None, project_shortname=None):
        """
        Join the sprint, with an optional starting word count and project shortname
        :param starting_wc:
        :param project_shortname:
        :return:
        """
        # user = User(context.message.author.id, context.guild.id, context)
        # sprint = Sprint(user.get_guild())
        #
        # # If there is no active sprint, then just display an error
        # if not sprint.exists():
        #     return await context.send(user.get_mention() + ', ' + lib.get_string('sprint:err:noexists', user.get_guild()))
        #
        # starting_wc = lib.is_number(starting_wc)
        # if starting_wc is False:
        #     starting_wc = 0
        #
        # # If the user is already sprinting, then just update their starting wordcount
        # if sprint.is_user_sprinting(user.get_id()):
        #     sprint.



    async def run_time(self, context):
        """
        Get how long is left in the sprint
        :param context:
        :return:
        """
        user = User(context.message.author.id, context.guild.id, context)
        sprint = Sprint(user.get_guild())

        # If there is no active sprint, then just display an error
        if not sprint.exists():
            return await context.send(user.get_mention() + ', ' + lib.get_string('sprint:err:noexists', user.get_guild()))

        now = int(time.time())

        # If the sprint has not yet started, display the time until it starts
        if not sprint.has_started():
            left = lib.secs_to_mins(sprint.start - now)
            return await context.send(user.get_mention() + ', ' + lib.get_string('sprint:startsin', user.get_guild()).format(left['m'], left['s']))

        # If it's currently still running, display how long is left
        elif not sprint.is_finished():
            left = lib.secs_to_mins(sprint.end - now)
            return await context.send(user.get_mention() + ', ' + lib.get_string('sprint:timeleft', user.get_guild()).format(left['m'], left['s']))

        # If it's finished but not yet marked as completed, we must be waiting for word counts
        elif sprint.is_finished():
            return await context.send(user.get_mention() + ', ' + lib.get_string('sprint:waitingforwc', user.get_guild()))


    async def run_notify(self, context):
        """
        Set a user to be notified of upcoming sprints on this server.
        :param context:
        :return:
        """
        user = User(context.message.author.id, context.guild.id, context)
        user.set_guild_setting('sprint_notify', 1)
        return await context.send(user.get_mention() + ', ' + lib.get_string('sprint:notified', user.get_guild()))

    async def run_forget(self, context):
        """
        Set a user to no longer be notified of upcoming sprints on this server.
        :param context:
        :return:
        """
        user = User(context.message.author.id, context.guild.id, context)
        user.set_guild_setting('sprint_notify', 0)
        return await context.send(user.get_mention() + ', ' + lib.get_string('sprint:forgot', user.get_guild()))

    async def run_cancel(self, context):
        """
        Cancel a running sprint on the server
        :param context:
        :return:
        """
        user = User(context.message.author.id, context.guild.id, context)
        sprint = Sprint(user.get_guild())

        # If there is no active sprint, then just display an error
        if not sprint.exists():
            return await context.send(user.get_mention() + ', ' + lib.get_string('sprint:err:noexists', user.get_guild()))

        # If they do not have permission to cancel this sprint, display an error
        if sprint.createdby != user.get_id() and context.message.author.permissions_in(context.message.channel).manage_messages is not True:
            return await context.send(user.get_mention() + ', ' + lib.get_string('sprint:err:cannotcancel', user.get_guild()))

        return await sprint.cancel(context)

    async def run_start(self, context, length=None, start=None):
        """
        Try to start a sprint on the server
        :param context
        :param length: Length of time (in minutes) the sprint should last
        :param start: Time in minutes from now, that the sprint should start
        :return:
        """
        user = User(context.message.author.id, context.guild.id, context)
        sprint = Sprint(user.get_guild())

        # Check if sprint is finished but not marked as completed, in which case we can mark it as complete
        if sprint.is_finished():
            # Mark the sprint as complete
            sprint.complete()
            # Reload the sprint object, as now there shouldn't be a pending one
            sprint = Sprint(user.get_guild())

        # If a sprint is currently running, we cannot start a new one
        if sprint.exists():
            return await context.send(user.get_mention() + ', ' + lib.get_string('sprint:err:alreadyexists', user.get_guild()))

        # Must be okay to continue #

        # If the length argument is not valid, use the default
        if length is None or lib.is_number(length) is False or lib.is_number(length) <= 0 or lib.is_number(length) > self.MAX_LENGTH:
            length = self.DEFAULT_LENGTH

        # Same goes for the start argument
        if start is None or lib.is_number(start) is False or lib.is_number(start) < 0 or lib.is_number(start) > self.MAX_DELAY:
            start = self.DEFAULT_DELAY

        # Make sure we are using ints and not floats passed through in the command
        length = int(length)
        start = int(start)

        # Calculate the start and end times based on the current timestamp
        now = int(time.time())
        start_time = now + (start * 60)
        end_time = start_time + (length * 60)

        # Create the sprint
        sprint = Sprint.create(guild=user.get_guild(), channel=context.message.channel.id, start=start_time, end=end_time, end_reference=end_time, length=length, createdby=user.get_id(), created=now)

        # Join the sprint
        sprint.join(user.get_id())

        # Increment the user's stat for sprints created
        user.add_stat('sprints_started', 1)

        # Are we starting immediately or after a delay?
        if start == 0:
            # Immediately
            return await sprint.post_start(context)
        else:
            # Delay
            return await sprint.post_delayed_start(context)


def setup(bot):
    bot.add_cog(SprintCommand(bot))