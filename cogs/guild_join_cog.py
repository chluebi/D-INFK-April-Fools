
import asyncio

import discord

from discord.ext import commands
from db import SQLiteDBManager
from db import DiscordUser

from constants import TransactionType
from events import on_score_update, score_update

class GuildJoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

            
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return
        db_user = self.db.get_discord_user(member.id)

        role = discord.utils.get(member.server.roles, id="957399970636509264")
        await self.bot.add_roles(member, role)

        if db_user is None:
            #TODO check Name and Nick
            self.db.create_discord_user(member.id, member.display_name, 1000, member.bot, False)
        else:
            await self.db.change_credits(member, TransactionType.escape_attempt)

# this code actually gets run when bot.load_extension(file) gets called on this file
# all cogs that should be loaded need to be added in here
def setup(bot: commands.Bot):
    bot.add_cog(GuildJoin(bot))
    