from pprint import pprint

import os, json, lib, discord, datetime, time
from discord.ext import commands

class About(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, aliases=['info'])
    async def about(self, context):
        """
        Displays information and statistics about the bot.
        Aliases: !info
        Examples: !about
        """

        now = time.time()
        uptime = int(round(now - self.bot.start_time))
        guild_id = context.guild.id
        config = self.bot.config

        # Begin the embedded message
        embed = discord.Embed(title=lib.get_string('info:bot', guild_id), color=3447003)
        embed.add_field(name=lib.get_string('info:version', guild_id), value=config.version, inline=True)
        embed.add_field(name=lib.get_string('info:uptime', guild_id), value=str(datetime.timedelta(seconds=uptime)), inline=True)

        # Statistics
        stats = []
        stats.append('• ' + lib.get_string('info:servers', guild_id) + ': ' + format(len(self.bot.guilds)))
        stats.append('• ' + lib.get_string('info:members', guild_id) + ': ' + format(self.count_members(self.bot.guilds)))
        stats.append('• ' + lib.get_string('info:sprints', guild_id) + ': TODO')
        stats.append('• ' + lib.get_string('info:helpserver', guild_id) + ': https://discord.gg/FbmaegR')
        stats = '\n'.join(stats)

        embed.add_field(name=lib.get_string('info:generalstats', guild_id), value=stats, inline=False)

        # Developer Info
        git = {}
        git['branch'] = os.popen(r'git rev-parse --abbrev-ref HEAD').read().strip()
        git['rev'] =  os.popen(r'git log --pretty=format:"%h | %ad | %s" --date=short -n 1').read().strip()

        dev = []
        dev.append(lib.get_string('info:dev:branch', guild_id) + ': ' + format(git['branch']))
        dev.append(lib.get_string('info:dev:repo', guild_id) + ': ' + format(config.src))
        dev.append(lib.get_string('info:dev:patch', guild_id) + ': ' + format(config.patch_notes))
        dev.append(lib.get_string('info:dev:change', guild_id) + ':\n\t' + format(git['rev']))
        dev = '\n'.join(dev)

        embed.add_field(name=lib.get_string('info:dev', guild_id), value=dev, inline=False)

        # Send the message
        await context.send(embed=embed)


    def count_members(self, guilds):
        """
        Count all the members in every server this bot is in.
        @param guilds: Passed from bot.guilds
        @return int Total member count
        """
        total = 0
        for guild in guilds:
            total += len(guild.members)
        return total


def setup(bot):
    bot.add_cog(About(bot))