from constants import TransactionType

class Transaction(object):

    def __init__(self, id, type_id, discord_user_id, amount, date_time, discord_message_id, discord_channel_id, reason, from_discord_user_id):
        self.id = id
        self.type_id = type_id
        self.type_name = TransactionType(type_id).name
        self.discord_user_id = discord_user_id
        self.amount = amount
        self.date_time = date_time
        self.discord_message_id = discord_message_id
        self.discord_channel_id = discord_channel_id
        self.reason = reason
        self.from_discord_user_id = from_discord_user_id