# library imports
import os
import logging
import traceback
import discord
from discord.ext import commands

# local imports
import util
import events

from db import SQLiteDBManager
from db import DiscordUser

discord_config = util.parse_config('discord')

# determining intents
intents = discord.Intents.all()

bot = commands.Bot(command_prefix=discord_config['prefix'], intents=intents)
bot.db = SQLiteDBManager(discord_config["db_path"], discord_config["backup_path"])

'''
basic logging

to log anything just import logging and do
logging.error(text)
or
logging.info(text)
'''
logging.basicConfig(handlers=[logging.FileHandler('bot.log', 'a', encoding='utf-8')],
                    format='%(asctime)s - %(levelname)s - %(message)s')


@bot.event
async def on_ready():
    print('------------------')
    print(f'bot ready {bot.user.name}')
    print('------------------')

# removing help command to hide funny commands
bot.remove_command('help')


@bot.event
async def on_command_error(ctx, error):
    error_message = ''.join(traceback.format_exception(
        type(error), error, error.__traceback__))
    logging.error(error_message)

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

    if (isinstance(error, commands.errors.UserNotFound) or isinstance(error, commands.errors.MemberNotFound)):
        await ctx.message.add_reaction('❌')
        return

    if (isinstance(error, commands.CommandOnCooldown)):
        await ctx.message.reply(f"Command on Cooldown. {int(error.retry_after)} seconds remaining...", delete_after=5)
        return
    
    if (isinstance(error, commands.errors.BadArgument)):
        await ctx.message.add_reaction('❌')
        return

    logging.error(error_message)


# setups the events file
# has to be done before the other cogs are loaded
events.setup(bot)

# iterate over all files in the "cogs folder"
for file in os.listdir('cogs'):
    if file == "__pycache__":
        continue
    import_path = 'cogs.' + file.split('.')[0]
    bot.load_extension(import_path)

# actually run the bot, this is blocking
bot.run(discord_config['token'])
