class DiscordUser(object):
    
    def __init__(self, discord_user_id, old_name, current_name, social_credit, is_bot, is_admin):
        self.discord_user_id = discord_user_id
        self.old_name = old_name
        self.current_name = current_name
        self.social_credit = social_credit
        self.is_bot = is_bot
        self.is_admin = is_admin