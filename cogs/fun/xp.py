import discord
from discord.ext import commands
from structures.user import User

class XP(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def xp(self, context, who='me'):
        """
        Checks your Experience Points and Level. Use the 'top' flag to see the top 10 on this server.
        Examples:
            !xp - Shows your level/xp
            !xp top - Shows the top 10 users on this server
        """

        guild_id = context.guild.id
        user_id = context.message.author.id

        if who == 'all':
            pass
        else:
            user = User(user_id, guild_id)
            xp = user.get_xp()


def setup(bot):
    bot.add_cog(XP(bot))