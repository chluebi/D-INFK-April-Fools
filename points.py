import discord
from db import SQLiteDBManager
from db import DiscordUser
from events import score_update

def change_points(member: discord.Member, delta_score: int, reason):
    #update db
    
    user = SQLiteDBManager.change_credits(member.id, 1, delta_score) 
    #change nick with new value, nick char limit = 32
    nick = user.current_name
    points = " [" + user.social_credit + "]"
    if nick.length + points.length > 32:
        nick[:32-points.length]
    nick += points
    member.edit(nick=nick)
    
    #send amount changed + reason into channel
    channel = member.guild.get_channel(954423559600631832)
    update = 'added' if points>0 else 'removed'
    channel.send(f'{member.mention} has gotten {points} {update}. Because of {reason}')
    
    score_update(member, user.social_credit)
    return