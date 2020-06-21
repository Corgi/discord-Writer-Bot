import os, logging, datetime, time, lib, traceback, discord
from discord.ext import tasks
from discord.ext import commands
from discord.ext.commands import AutoShardedBot
from structures.db import *
from structures.guild import Guild
from structures.task import Task
from structures.user import User

from pprint import pprint

class WriterBot(AutoShardedBot):

    COMMAND_GROUPS = ['util', 'fun', 'writing']
    SCHEDULED_TASK_LOOP = 30.0 # Seconds
    CLEANUP_TASK_LOOP = 1.0 # Hours

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = lib.get('./settings.json')
        self.start_time = time.time()
        self.app_info = None
        self.setup()

    async def on_message(self, message):
        """
        Run any checks we need to, before processing the messages.
        :param message:
        :return:
        """
        # If the bot is not logged in yet, don't try to run any commands.
        if not self.is_ready():
            return

        await self.process_commands(message)

    async def on_ready(self):
        """
        Method run once the bot has logged in as is ready to be used.
        :return:
        """
        lib.debug('Logged on as: ' + str(self.user))

        # Show the help command on the status
        await self.change_presence(activity=discord.Game(self.config.prefix + 'help'))

        # Retrieve app info.
        self.app_info = await self.application_info()

        # Start running the scheduled tasks.
        self.scheduled_tasks.start()
        self.cleanup_tasks.start()

    async def on_command_error(self, context, error):
        """
        Method to run if there is an exception thrown by a command
        :param error:
        :param context:
        :return:
        """
        user = User(context.message.author.id, context.guild.id, context)

        ignore = (commands.errors.CommandNotFound, commands.errors.UserInputError)

        if isinstance(error, ignore):
            return
        elif isinstance(error, commands.errors.NoPrivateMessage):
            return await context.send('Commands cannot be used in Private Messages.')
        elif isinstance(error, commands.errors.MissingPermissions):
            return await context.send(user.get_mention() + ', ' + str(error))
        else:
            lib.error('Exception in command `{}`: {}'.format(context.command, str(error)))
            lib.error( traceback.format_exception(type(error), error, error.__traceback__) )
            return await context.send(lib.get_string('err:unknown', user.get_guild()))

    def load_commands(self):
        """
        Load all the commands from the cogs/ directory.
        :return: void
        """
        # Find all the command groups in the cogs/ directory
        for dir in self.COMMAND_GROUPS:

            # Then all the files inside the command group directory
            for file in os.listdir(f'cogs/{dir}'):

                # If it ends with .py then try to load it.
                if file.endswith(".py"):

                    cog = file[:-3]

                    try:
                        self.load_extension(f"cogs.{dir}.{cog}")
                        print(f'[EXT][{dir}.{cog}] loaded')
                    except Exception as e:
                        print(f'[EXT][{dir}.{cog}] failed to load')
                        print(e)

    def setup(self):
        """
        Run the bot setup
        :return:
        """
        # Install the database.
        db = Database.instance()
        db.install()
        print('[DB] Database tables installed')

        # Setup the recurring tasks which need running.
        self.setup_recurring_tasks()
        print('[TASK] Recurring tasks inserted')

        # Restart all tasks which are marked as processing, in case the bot dropped out during the process.
        db.update('tasks', {'processing': 0})

    def setup_recurring_tasks(self):
        """
        Create the recurring tasks for the first time.
        :return:
        """
        db = Database.instance()

        # Delete the recurring tasks in case they got stuck in processing, and then re-create them.
        db.delete('tasks', {'object': 'goal', 'type': 'reset'})
        db.insert('tasks', {'object': 'goal', 'time': 0, 'type': 'reset', 'recurring': 1, 'runeveryseconds': 900})

    @staticmethod
    def load_prefix(bot, message):
        """
        Get the prefix to use for the guild
        :param bot:
        :param message:
        :return:
        """
        db = Database.instance()
        prefixes = {}
        config = lib.get('./settings.json')

        # Get the guild_settings for prefix and add to a dictionary, with the guild id as the key.
        settings = db.get_all('guild_settings', {'setting': 'prefix'})
        for setting in settings:
            prefixes[int(setting['guild'])] = setting['value']

        # If the guild id exists in this dictionary return that, otherwise return the default.
        if message.guild is not None:
            return prefixes.get(message.guild.id, config.prefix)
        else:
            return config.prefix

    @tasks.loop(seconds=SCHEDULED_TASK_LOOP)
    async def scheduled_tasks(self):
        """
        Execute the scheduled tasks.
        (I believe) this is going to happen for each shard, so if we have 5 shards for example, this loop will be running simultaneously on each of them.
        :return:
        """
        lib.debug('['+str(self.shard_id)+'] Checking for scheduled tasks...')

        try:
            await Task.execute_all(self)
        except Exception as e:
            print('Exception: ' + str(e))

    @tasks.loop(hours=CLEANUP_TASK_LOOP)
    async def cleanup_tasks(self):
        """
        Clean up any old tasks which are still in the database and got stuck in processing
        :return:
        """
        db = Database.instance()

        lib.debug('['+str(self.shard_id)+'] Running task cleanup...')

        hour_ago = int(time.time()) - (60*60)
        db.execute('DELETE FROM tasks WHERE processing = 1 AND time < %s', [hour_ago])

