import asyncio

import discord

from discord.ext import commands
from db import SQLiteDBManager
from db import DiscordUser

from constants import TransactionType
from events import on_score_update, score_update

class Role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

            
    #updates the user with the correct role again after a score change
    @on_score_update
    async def timeout(self, member: discord.Member, user: DiscordUser, delta_score: int, reason):
        if user.social_credit > 0 or member.messenger.guild_permissions.admin:
            return
        channel = member.guild.get_channel(34234)
        channel.send(f'timeout: {member.id} This is a timeout for {member.mention}')
        amount = -1 * user.social_credit + 250
        await self.db.change_credits(member=member, TransactionType=TransactionType.timeout, amount=amount, reason="Timeout")
        

# this code actually gets run when bot.load_extension(file) gets called on this file
# all cogs that should be loaded need to be added in here
def setup(bot: commands.Bot):
    bot.add_cog(Role(bot))
