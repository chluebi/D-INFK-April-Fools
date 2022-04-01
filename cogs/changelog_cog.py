import discord
from discord.ext import commands
from events import on_score_update


CHANGELOG_CHANNEL = 955085185593008209
POS_SCORE_EMOTE = "<:up:955093895505653800>"
NEG_SCORE_EMOTE = "<:down:955093895748935730>"

# sends the score updates into the changelog channel

@on_score_update
async def send_update(bot, member, user, delta_score, reason):
    # ignore score changes that are less than 5
    if abs(delta_score) < 10:
        return

    color = discord.Color.green()
    emote = POS_SCORE_EMOTE
    if delta_score < 0:
        color = discord.Color.red()
        emote = NEG_SCORE_EMOTE

    if len(reason) == 0:  # can't send empty fields on discord
        reason = "*no reason*"

    embed = discord.Embed(color=color)
    embed.add_field(name="Score Update",
                    value=f"Score: `{user.social_credit}`")
    embed.add_field(name="‎", value=f"{emote} `{delta_score}`")
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_footer(text=str(member), icon_url=member.avatar_url)

    changelog_channel_id = bot.db.get_key("ChangelogChannelId")
    channel = bot.get_channel(changelog_channel_id)
    await channel.send(embed=embed)


def setup(bot: commands.Bot):
    pass
