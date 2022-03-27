import re
import discord

from discord.ext import commands
from db import SQLiteDBManager
from db import DiscordUser

from constants import TransactionType
from events import on_score_update, score_update

class Rename(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @commands.Cog.listener()
    async def on_member_update(self, before, after):

        enable_rename = self.db.get_key("EnforceNameChange")
        enable_rename = True

        if enable_rename is False:
            return

        if before.display_name != after.display_name:
            user = self.db.get_discord_user(after.id)
            score = f" [{user.social_credit}]"

            #if Nickname still has score, dont change but save new nickname into db
            cleaned_nick = re.sub(r"\[\d+\]", "", after.display_name).strip()
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
        # Reload the new credits
        score = f" [{user.social_credit}]"
        new_name = user.current_name[:25]+score
        await member.edit(nick=new_name)
            
        
def setup(bot: commands.Bot):
    bot.add_cog(Rename(bot))
