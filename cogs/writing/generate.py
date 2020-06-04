import discord, lib
from discord.ext import commands
from structures.generator import NameGenerator
from structures.user import User
from structures.wrapper import CommandWrapper

class Generate(commands.Cog, CommandWrapper):

    def __init__(self, bot):
        self.bot = bot
        self._supported_types = ['char', 'place', 'land', 'idea', 'book', 'book_fantasy', 'book_horror', 'book_hp', 'book_mystery', 'book_rom', 'book_sf']
        self._arguments = [
            {
                'key': 'type',
                'prompt': 'generate:argument:type',
                'required': True,
                'check': lambda content : content in self._supported_types,
                'error': 'generate:err:type'
            },
            {
                'key': 'amount',
                'required': False,
                'prompt': 'generate:argument:amount',
                'type': int
            }
        ]

    @commands.command(name="generate")
    async def generate(self, context, type=None, amount=None):
        """
        Random generator for various things (character names, place names, land names, book titles, story ideas).
        Define the type of item you wanted generated and then optionally, the amount of items to generate.

        Examples:
            !generate char !generates 10 character names
            !generate place 20 !generates 20 fantasy place names
            !generate land !generates 10 fantasy land/world names
            !generate book !generates 10 general fiction book titles
            !generate book_fantasy !generates 10 fantasy book titles
            !generate book_sf !generates 10 sci-fi book titles
            !generate book_horror !generates 10 horror book titles
            !generate book_rom !generates 10 romance/erotic book titles
            !generate book_mystery !generates 10 mystery book titles
            !generate book_hp !generates 10 Harry Potter book title
            !generate idea !generates a random story idea
        """

        user = User(context.message.author.id, context.guild.id, context)

        # If no amount specified, use the default
        if amount is None:
            amount = NameGenerator.DEFAULT_AMOUNT

        # Check the arguments are valid
        args = await self.check_arguments(context, type=type, amount=amount)
        if not args:
            return

        type = args['type'].lower()
        amount = int(args['amount'])

        generator = NameGenerator(type, context)
        results = generator.generate(amount)
        names = '\n'.join(results['names'])

        return await context.send(user.get_mention() + ', ' + results['message'] + names)



def setup(bot):
    bot.add_cog(Generate(bot))