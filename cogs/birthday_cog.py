import asyncio

import discord
import events
from discord.ext import commands
from db import SQLiteDBManager

from bot import discord_config

class Birthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = SQLiteDBManager(discord_config["db_path"])

    #when I react with peepolove it gives points
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == 223932775474921472: #id of EvilBabyDemon
            if payload.emoji.name == "peepolove":
                #transactiontype ID 4 probably will change still
                self.db.change_credits(payload.member.id, 4, payload.message_id, payload.channel_id)
            

# this code actually gets run when bot.load_extension(file) gets called on this file
# all cogs that should be loaded need to be added in here
def setup(bot: commands.Bot):
    bot.add_cog(Birthday(bot))
