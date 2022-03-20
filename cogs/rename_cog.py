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
    async def on_member_update(self, before, after):
        if before.display_name != after.display_name:
            user = self.db.get_discord_user(after.id)
            score = " [" + str(user.social_credit) + "]"
            #if Nickname still has score, dont change but save new nickname into db

            if after.display_name.endswith(score):
                current = after.display_name
                current = current.removesuffix(score)
                self.db.rename_discord_user(after.id, current)
                return

            self.db.change_credits(after.id, TransactionType.invalid_name_change, reason=f"Faulty rename from '{before.nick}' to '{after.nick}'") 
            # Reload the new credits TODO check if change_credits returns user updated
            user = self.db.get_discord_user(after.id)
            score = " [" + str(user.social_credit) + "]"
            new_name = user.current_name[:25]+score
            print(new_name)
            await after.edit(nick=new_name)
            
            

# this code actually gets run when bot.load_extension(file) gets called on this file
# all cogs that should be loaded need to be added in here
def setup(bot: commands.Bot):
    bot.add_cog(Rename(bot))
