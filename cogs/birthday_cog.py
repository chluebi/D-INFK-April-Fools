import asyncio

import discord
from cogs.basic_cog import Cog
import events
from discord.ext import commands
from db import SQLiteDBManager

from points import change_points

class Birthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #when I react with peepolove it gives points
    @commands.Cog.listener()
    async def on_raw_reaction_add(payload):
        if payload.user_id == 223932775474921472: #id of EvilBabyDemon
            if payload.emoji.name == "peepolove":
                #transactiontype ID 4 probably will change still
                SQLiteDBManager.change_credits(payload.member.id, 4)
            

# this code actually gets run when bot.load_extension(file) gets called on this file
# all cogs that should be loaded need to be added in here
def setup(bot: commands.Bot):
    bot.add_cog(Birthday(bot))
