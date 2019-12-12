import os
import logging
from discord.ext.commands import AutoShardedBot

class WriterBot(AutoShardedBot):

    COMMAND_GROUPS = ['util', 'fun', 'writing']

    def __init__(self, *args, prefix=None, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print('Logged on as', self.user)

    def load_commands(self):
        """
        Load all the commands from the cogs/ directory.
        @return: void
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
