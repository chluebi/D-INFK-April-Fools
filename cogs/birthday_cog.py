import asyncio

import discord
import events
from discord.ext import commands
from db import SQLiteDBManager

from bot import discord_config

class Birthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    #when I react with peepolove it gives points
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == 223932775474921472: #id of EvilBabyDemon
            if payload.member is not None:
                if payload.emoji.name == "peepolove":
                    #transactiontype ID 4 probably will change still
                    messenger = payload.member.guild.get_channel(payload.channel_id).fetch_message(payload.message_id).author
                    self.db.change_credits(payload.member.guild, 4, payload.message_id, payload.channel_id)
                

# this code actually gets run when bot.load_extension(file) gets called on this file
# all cogs that should be loaded need to be added in here
def setup(bot: commands.Bot):
    bot.add_cog(Birthday(bot))
