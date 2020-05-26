import asyncio
import lib

class CommandWrapper:

    TIMEOUT_WAIT=10

    def __init__(self):
        self._arguments = []
        pass

    async def check_arguments(self, context, **kwargs):

        # Loop through the arguments we defined in the __init__ of the command class
        for arg in self._arguments:

            # If we found that argument in the arguments passed through in the command check, then we can check it
            if arg['key'] in kwargs:

                # Get the value passed into this function for checking
                value = kwargs[arg['key']]

                # If the argument is required and the value is invalid, then prompt for a value
                if arg['required'] and not value:

                    response = await self.prompt(context, arg['prompt'])
                    if response:
                        kwargs[arg['key']] = response.content
                    else:
                        return False

        return kwargs

    async def prompt(self, context, message):

        # Check if the response is from the same user, in the same channel.
        def check(msg):
            return msg.author == context.author and msg.channel == context.channel

        # Send the prompt message and wait for a reply
        message = lib.get_string(message, context.guild.id)
        req = await context.send(f'{context.author.mention}, {message}')
        try:
            response = await self.bot.wait_for('message', check=check, timeout=self.TIMEOUT_WAIT)
            return response
        except asyncio.TimeoutError:
            await req.edit(content='Request for command argument timed out')
            return False


# @commands.command()
# async def foo(ctx, bar=None):
#   if bar is None:
#     req = await ctx.send(f'{ctx.author.mention}: please supply arg bar')
#     try:
#       msg = await ctx.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=30)
#     except asyncio.TimeoutError:
#       await req.edit(content='Request for arg bar timed out')
#       return
#     bar = msg.content
#   ...  # rest of command