# library imports
import os
import logging
import traceback
import nextcord
from nextcord.ext import commands

# local imports
import util

discord_config = util.parse_config('discord')

# determining intents
intents = nextcord.Intents.default()
intents.members = True
# intents.presences = True

bot = commands.Bot(command_prefix='{0} '.format(discord_config['prefix']), intents=intents)

'''
basic logging

to log anything just import logging and do
logging.error(text)
or
logging.info(text)
'''
logging.basicConfig(handlers=[logging.FileHandler('bot.log', 'a', encoding='utf-8')], format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

@bot.event
async def on_ready():
    print('------------------')
    print(f'bot ready {bot.user.name}')
    print('------------------')

# removing help command to hide funny commands
bot.remove_command('help')

@bot.event
async def on_command_error(ctx, error):
    error_message = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
    
    # ignoring errors that do not need to be logged
    if (isinstance(error, commands.CommandNotFound)):
        await ctx.message.add_reaction('❌')
        return

    if (isinstance(error, commands.CheckFailure)):
        await ctx.message.add_reaction('❌')
        return

    if (isinstance(error, commands.MissingRequiredArgument)):
        await ctx.message.add_reaction('❌')
        return

    if (isinstance(error, commands.errors.UserNotFound)):
        await ctx.message.add_reaction('❌')
        return

    logging.error(error_message)

# iterate over all files in the "cogs folder"
for file in os.listdir('cogs'):
    import_path = 'cogs.' + file.split('.')[0]
    bot.load_extension(import_path)

# actually run the bot, this is blocking
bot.run(discord_config['token'])