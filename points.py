import discord
from db import SQLiteDBManager
from db import DiscordUser

def change_points(member: discord.Member, delta_score: int, reason):
    user = SQLiteDBManager.update_points(member.id, delta_score) 
    nick = user.old_name
    points = " [" + user.social_credit + "]"
    if nick.length + points.length > 32:
        nick[:32-points.length]
    nick += points
    member.edit(nick=nick)
    
    #send amount changed + reason into channel
    channel = member.guild.get_channel(954423559600631832)
    update = 'added' if points>0 else 'removed'
    channel.send(f'{member.mention} has gotten {points} {update}. Because of {reason}')
    return