import random
import re
import lib
import discord
from discord.ext import commands
from structures.db import Database
from structures.user import User
from structures.wrapper import CommandWrapper

class Challenge(commands.Cog, CommandWrapper):

    WPM={'min': 5, 'max': 30}
    TIMES={'min': 5, 'max': 60}

    def __init__(self, bot):
        self.bot = bot
        self.__db = Database.instance()
        self._arguments = [
            {
                'key': 'flag',
            }
        ]

    @commands.command(name="challenge")
    @commands.guild_only()
    async def ask(self, context, flag=''):
        """
        Generates a random writing challenge for you. e.g. "Write 400 words in 15 minutes".
        You can add the flags "easy", "normal", "hard", "hardcore", or "insane" to choose a pre-set wpm,
        or add your chosen wpm (words per minute) as the flag, suffixed with "wpm", eg. "30wpm",
        or you can specify a time instead by adding a the time in minutes, suffixed with a "m", e.g. "15m".

        If you do not specify any flags with the command, the challenge will be completely random.

        Examples:
            !challenge cancel - Cancels your current challenge,
            !challenge done|complete - Completes your current challenge,

            !challenge - Generates an entirely random writing challenge,
            !challenge easy - Generates a random writing challenge, at 5 wpm (20xp),
            !challenge normal - Generates a random writing challenge, at 10 wpm (40xp),
            !challenge hard - Generates a random writing challenge, at 20 wpm (75xp),
            !challenge hardcore - Generates a random writing challenge, at 40 wpm (100xp),
            !challenge insane - Generates a random writing challenge, at 60 wpm (150xp),
            !challenge 10wpm - Generates a random writing challenge, at 10 wpm,
            !challenge 15m - Generates a random writing challenge, with a duration of 15 minutes
        """

        flag = flag.lower()

        if flag == 'cancel':
            await self.run_cancel(context)
        elif flag == 'done' or flag == 'complete':
            await self.run_complete(context)
        else:
            await self.run_challenge(context, flag)

    def calculate_xp(self, wpm):
        """
        Calculate the XP to give for the challenge, based on the words per minute.
        """

        if wpm <= 5:
            return 20
        elif wpm <= 10:
            return 40
        elif wpm <= 20:
            return 75
        elif wpm <= 40:
            return 100
        elif wpm <= 60:
            return 150
        elif wpm > 60:
            return 200

    async def run_complete(self, context):

        user = User(context.message.author.id, context.guild.id, context)

        # Do they have an active challenge to mark as complete?
        challenge = user.get_challenge()
        if challenge:

            # Update the challenge with the time completed
            user.complete_challenge(challenge['id'])

            # Add the XP
            await user.add_xp(challenge['xp'])

            # Increment the challenges_completed stat
            user.add_stat('challenges_completed', 1)

            output = lib.get_string('challenge:completed', user.get_guild()) + ' **' + challenge['challenge'] + '**          +' + str(challenge['xp']) + 'xp'

        else:
            output = lib.get_string('challenge:noactive', user.get_guild())

        await context.send(f'{context.message.author.mention}, {output}')


    async def run_cancel(self, context):

        user = User(context.message.author.id, context.guild.id, context)
        challenge = user.get_challenge()

        if challenge:
            user.delete_challenge()
            output = lib.get_string('challenge:givenup', user.get_guild())
        else:
            output = lib.get_string('challenge:noactive', user.get_guild())

        await context.send(f'{context.message.author.mention}, {output}')

    async def run_challenge(self, context, flag):

        user = User(context.message.author.id, context.guild.id, context)

        challenge = user.get_challenge()
        if challenge:
            output = lib.get_string('challenge:current', user.get_guild()) + ': **' + \
                     challenge['challenge'] + '**\n' + \
                     lib.get_string('challenge:tocomplete', user.get_guild())
            await context.send(f'{context.message.author.mention}, {output}')
            return


        # First create a random WPM and time and then adjust if they are actually specified
        wpm = random.randint(self.WPM['min'], self.WPM['max'])
        time = random.randint(self.TIMES['min'], self.TIMES['max'])

        if flag == 'easy':
            wpm = 5
        elif flag == 'normal':
            wpm = 10
        elif flag == 'hard':
            wpm = 20
        elif flag == 'hardcore':
            wpm = 40
        elif flag == 'insane':
            wpm = 60
        elif flag.isdigit():
            # If it's just a digit, assume that's the WPM
            wpm = int(flag)
        elif flag.endswith('wpm'):
            # If it ends with 'wpm' remove that and convert to an int for the WPM
            wpm = int(re.sub(r'\D', '', flag))
        elif flag.endswith('m'):
            # If it ends with 'm' remove that and convert to an int for the time
            time = int(re.sub(r'\D', '', flag))

        goal = wpm * time
        xp = self.calculate_xp(wpm)

        challenge = lib.get_string('challenge:challenge', user.get_guild()).format(words=goal, mins=time, wpm=wpm)
        message = challenge + '\n'
        message += lib.get_string('challenge:decide', user.get_guild())

        # Build a fake argument, as the argument is optional so isn't checked by the normal check_arguments method
        argument = {'prompt': message, 'check': lambda resp : resp.lower() in ('y', 'yes', 'n', 'no')}

        # Print the challenge and ask for confirmation response
        response = await self.prompt(context, argument, True)
        if not response:
            return

        response = response.content

        # If they accept it, set the challenge and print the message
        if response.lower() in ('y', 'yes'):
            user.set_challenge(challenge, xp)
            output = lib.get_string('challenge:accepted', user.get_guild()) + ' **' + challenge + '**\n' + lib.get_string('challenge:tocomplete', user.get_guild())
        else:
            # Otherwise, just print 'OK'
            output = 'OK'

        await context.send(context.message.author.mention + ', ' + output)

def setup(bot):
    bot.add_cog(Challenge(bot))