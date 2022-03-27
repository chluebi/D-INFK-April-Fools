import asyncio
import re
import discord

from time import time

from discord.ext import commands
from db import DiscordUser

from constants import TransactionType
from events import on_score_update, score_update


# dict of when a user was last renamed
last_renamed = {}
rename_to = {}


class Rename(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @commands.Cog.listener()
    async def on_member_update(self, before, after):

        enable_rename = self.db.get_key("RemovePointsOnRename")
        enable_rename = True

        if enable_rename is None:
            print("\033[31mKey RemovePointsOnRename has not been set for rename_cog.py\033[0m | Not checking name renames")
            return
        if not enable_rename:
            return

        if before.display_name != after.display_name:
            user = self.db.get_discord_user(after.id)
            score = f" [{user.social_credit}]"

            #if Nickname still has score, dont change but save new nickname into db
            cleaned_nick = re.sub(r"\[-?\d+\]", "", after.display_name).strip()
            if after.display_name.endswith(score):
                # simply removes all [number] things in a name
                reduce_credits = False
                self.db.rename_discord_user(after.id, cleaned_nick)
            else:
                reduce_credits = True
                
            # we generate the new username. If the previous step cleared it all, we choose a placeholder name
            if len(cleaned_nick) == 0:
                cleaned_nick = f"Loyal Citizen #{after.discriminator}"
            new_nick = cleaned_nick[:25] + score
            # if the above removal of numbers resulted in a new username. change it
            if new_nick!= after.display_name:  
                await after.edit(nick=new_nick)

            if reduce_credits:
                await self.db.change_credits(after, TransactionType.invalid_name_change, reason=f"Faulty rename from '{before.display_name}' to '{after.display_name}'") 
            
    #updates the user with the correct score again, if there score got updated or they did a faulty rename
    @on_score_update
    async def rename_member(bot, member: discord.Member, user: DiscordUser, delta_score: int, reason):
        should_rename = bot.db.get_key("ScoreNameChange")
        if should_rename is None:
            print("\033[31mKey ScoreNameChange has not been set for rename_cog.py\033[0m | Not renaming any users now")
            return
        if not should_rename:
            return
        
        if member == member.guild.owner:
            return
        
        # backdoor, so worst case after 3 minutes
        # the name can be changed again
        CUTOFF_SECONDS = 180 
        
        score = f" [{user.social_credit}]"
        new_name = user.current_name[:25]+score
        rename_to[member.id] = new_name
        
        if member.id in last_renamed:
            last_renamed[member.id] = time()
            # if the member was recently renamed, let the first thread "handle it"
            if last_renamed[member.id] > time() - CUTOFF_SECONDS:
                return
        
        last_renamed[member.id] = time()
        # if there are more people waiting for their name to be changed (more people are spamming)
        # wait a longer time until their name is changed to avoid too much rate limitting
        while time() - (5 + len(rename_to) * 5) < last_renamed[member.id]:
            await asyncio.sleep(5)
        last_renamed.pop(member.id)
        await member.edit(nick=rename_to[member.id])
            
        
def setup(bot: commands.Bot):
    bot.add_cog(Rename(bot))
