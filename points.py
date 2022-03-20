import discord
from db import DiscordUser
from events import on_score_update

@on_score_update
async def send_update(bot, member, user, delta_score, reason):
    channel = bot.get_channel(954423559600631832)
    await channel.send(f"{str(user)}'s score was changed to {user.social_credit}")
    """"
    #send amount changed + reason into channel
    channel = member.guild.get_channel(954423559600631832)
    update = 'added' if points>0 else 'removed'
    channel.send(f'{member.mention} has gotten {points} {update}. Because of {reason}')
    """
    
@on_score_update
async def send_update(bot, member, user, delta_score, reason):
    #change nick with new value, nick char limit = 32
    nick = user.current_name
    points = " [" + user.social_credit + "]"
    if nick.length + points.length > 32:
        nick[:32-points.length]
    nick += points
    member.edit(nick=nick)