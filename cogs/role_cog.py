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
    async def give_role(bot, member: discord.Member, user: DiscordUser, delta_score: int, reason):
                
        score = user.social_credit
        if score > 2000:
            score = 2000
        if score < 0:
            score = 0
        
        role_score = int(member.top_role.name)    
        if role_score <= score & score <= role_score+99:
            return
        
        new_role = None
        for role in member.guild.roles:
            if role.name.isdigit() & int(role.name)==score:
                new_role = role
                break
        
        member.remove_roles(member.top_role)
        if new_role != None:
            member.add_roles(new_role)
        

# this code actually gets run when bot.load_extension(file) gets called on this file
# all cogs that should be loaded need to be added in here
def setup(bot: commands.Bot):
    bot.add_cog(Role(bot))
