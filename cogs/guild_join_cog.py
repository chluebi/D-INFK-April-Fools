
from discord.ext import commands

from constants import TransactionType


class GuildJoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return
        db_user = self.db.get_discord_user(member.id)

        role = member.guild.get_role(957399970636509264)
        await member.add_roles(role)

        if db_user is None:
            # TODO check Name and Nick
            self.db.create_discord_user(
                member.id, member.display_name, 1000, member.bot, False)
        else:
            await self.db.change_credits(member, TransactionType.escape_attempt)

# this code actually gets run when bot.load_extension(file) gets called on this file
# all cogs that should be loaded need to be added in here


def setup(bot: commands.Bot):
    bot.add_cog(GuildJoin(bot))
