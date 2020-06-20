import discord, lib
from discord.ext import commands
from structures.user import User
from structures.wrapper import CommandWrapper

class Admin(commands.Cog, CommandWrapper):

    def __init__(self, bot):
        self.bot = bot
        self._supported_commands = ['status']
        self._arguments = [
            {
                'key': 'cmd',
                'prompt': 'admin:argument:cmd',
                'required': True,
                'check': lambda content: content in self._supported_commands,
                'error': 'admin:err:argument'
            }
        ]

    @commands.command(name="admin")
    @commands.guild_only()
    async def admin(self, context, cmd=None, *opts):
        """
        Runs admin commands on the bot
        :param context:
        :param opts:
        :return:
        """

        user = User(context.message.author.id, context.guild.id, context=context, bot=self.bot)
        if not user.is_owner():
            raise commands.errors.MissingPermissions(['Bot owner'])

        # Check the arguments were all supplied and get a dict list of them and their values, after any prompts
        args = await self.check_arguments(context, cmd=cmd)
        if not args:
            return

        # Overwrite the variables passed in, with the values from the prompt and convert to lowercase
        cmd = args['cmd'].lower()

        if cmd == 'status':
            return await self.run_status(context, opts)


    async def run_status(self, context, opts):
        """
        Change the bot's status
        :param opts:
        :return:
        """
        status = " ".join(opts[0:])
        return await self.bot.change_presence(activity=discord.Game(status))

def setup(bot):
    bot.add_cog(Admin(bot))