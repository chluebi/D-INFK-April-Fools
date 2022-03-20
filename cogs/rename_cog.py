import asyncio

import discord
import events
from discord.ext import commands
from db import SQLiteDBManager
from db import DiscordUser

from constants import TransactionType


class Rename(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    #when I react with peepolove it gives points
    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if before.nick != after.nick:
            user = self.db.get_discord_user(after.id)
            score = " [" + user.social_credit + "]"
            
            #if Nickname still has score, dont change but save new nickname into db
            if after.nick.endsWith(score):
                current = after.nick
                current = current.removesuffix(score)
                self.db.rename_discord_user(after.member_id, current)
                return
            self.db.change_credits(after, TransactionType.invalid_name_change, -20, "faulty rename") 
            
            

# this code actually gets run when bot.load_extension(file) gets called on this file
# all cogs that should be loaded need to be added in here
def setup(bot: commands.Bot):
    bot.add_cog(Rename(bot))
