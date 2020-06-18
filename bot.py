import os, logging, datetime, time, lib
from discord.ext import tasks
from discord.ext.commands import AutoShardedBot
from structures.db import *
from structures.task import Task

from pprint import pprint

class WriterBot(AutoShardedBot):

    COMMAND_GROUPS = ['util', 'fun', 'writing']
    SCHEDULED_TASK_LOOP = 5.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = lib.get('./settings.json')
        self.start_time = time.time()
        self.app_info = None
        self.setup()

    async def on_ready(self):
        """
        Method run once the bot has logged in as is ready to be used.
        :return:
        """
        lib.debug('Logged on as: ' + str(self.user))

        # Retrieve app info.
        self.app_info = await self.application_info()

        # Start running the scheduled tasks.
        self.scheduled_tasks.start()

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

    def setup_recurring_tasks(self):
        """
        Create the recurring tasks for the first time.
        :return:
        """
        db = Database.instance()

        # Delete the recurring tasks in case they got stuck in processing, and then re-create them.
        db.delete('tasks', {'object': 'goal', 'type': 'reset'})
        db.insert('tasks', {'object': 'goal', 'time': 0, 'type': 'reset', 'recurring': 1, 'runeveryseconds': 900})

    @tasks.loop(seconds=SCHEDULED_TASK_LOOP)
    async def scheduled_tasks(self):
        """
        Execute the scheduled tasks.
        (I believe) this is going to happen for each shard, so if we have 5 shards for example, this loop will be running simultaneously on each of them.
        :return:
        """
        lib.debug('['+str(self.shard_id)+'] Checking for scheduled tasks...')

        # try:
        await Task.execute_all(self)
        # except Exception as e:
        #     print('Exception: ' + str(e))