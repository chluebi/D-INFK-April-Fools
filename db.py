import sqlite3
from sqlite3 import Error
import traceback

class DiscordUser(object):

    def __init__(self, discord_user_id, old_name, current_name, social_credit, is_bot, is_admin):
        self.discord_user_id = discord_user_id
        self.old_name = old_name
        self.current_name = current_name
        self.social_credit = social_credit
        self.is_bot = is_bot
        self.is_admin = is_admin

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class SQLiteDBManager(object, metaclass=Singleton):

    def __init__(self, path=None):
        self._path = path

        self.dbON = False 
        self._conn = None
        self._c = None

        #traceback.print_stack()

        try:
            db_fname = self._path
            print("---- Connecting to {}".format(db_fname))
            self._conn = sqlite3.connect(db_fname)
            self._c = self._conn.cursor()
            self.dbON = True

            self.initalize_tables()
            self.insert_transaction_types()
        except:
            print("---- Error connecting to the database")

    def __del__(self):
        """
        When destroying the object, it is necessary to commit changes
        in the database and close the connection
        """

        try:
            self._conn.commit()
            self._conn.close()
        except:
            print("---- Error closing database")

        return

    def initalize_tables(self):

        sql_queries = []

        sql_queries.append(""" CREATE TABLE IF NOT EXISTS DiscordUsers (
                                        DiscordUserId INT UNIQUE,
                                        OldUsername TEXT NOT NULL,
                                        CurrentUsername TEXT NOT NULL,
                                        SocialCredit INTEGER NULL,
                                        IsBot INTEGER NOT NULL,
                                        IsAdmin INTEGER NOT NULL DEFAULT 0
                                    ); """)

        sql_queries.append(""" CREATE TABLE IF NOT EXISTS SocialCreditTransactionTypes (
                                        SocialCreditTransactionTypeId INT UNIQUE,
                                        Name TEXT NOT NULL,
                                        DefaultAmount INTEGER NULL,
                                        AllowOnce INTEGER DEFAULT 0
                                    ); """)

        sql_queries.append("""CREATE TABLE IF NOT EXISTS SocialCreditTransactions (
                                    SocialCreditTransactionId INTEGER PRIMARY KEY AUTOINCREMENT,
                                    Amount INTEGER NOT NULL,
                                    DiscordUserId INTEGER NOT NULL,
                                    SocialCreditTransactionTypeId INTEGER NOT NULL,
                                    DiscordMessageId INTEGER NOT NULL,
                                    DiscordChannelId INTEGER NOT NULL,
                                    Reason TEXT NULL,
                                    FOREIGN KEY (DiscordUserId) REFERENCES DiscordUsers (DiscordUserId),
                                    FOREIGN KEY (SocialCreditTransactionTypeId) REFERENCES SocialCreditTransactionTypes (SocialCreditTransactionId)
                                );""")

        try:
            c = self._conn.cursor()

            for query in sql_queries:
                c.execute(query)

            self._conn.commit()
        except Error as e:
            print(e)


    def insert_transaction_types(self):

        # TODO Check if exists

        sql = f"""INSERT INTO SocialCreditTransactionTypes (SocialCreditTransactionTypeId, Name, DefaultAmount, AllowOnce)
        VALUES 
        (1, 'AdminChange', NULL, 0),
        (2, 'ReactionUp', 1, 0),
        (3, 'ReactionDown', -1, 0),
        (4, 'BirthdayWish', 20, 1)"""

        try:
            c = self._conn.cursor()
            c.execute(sql)
            self._conn.commit()
        except Error as e:
            print(e)


    def sql_query(self, query):
        output = ""

        try:
            c = self._conn.cursor()
            c.execute(query)

            results = c.fetchmany(50)
            #print(results)
            #print(result)
            for result in results:
                output = output + str(result) + "\r\n"

            return output
        except Error as e:
            print(e)


    def get_discord_user(self, discord_user_id):

        sql = f"""SELECT 
            DiscordUserId,
            OldUsername,
            CurrentUsername,
            SocialCredit,
            IsBot,
            IsAdmin 
        FROM DiscordUsers WHERE DiscordUserId = {discord_user_id}"""

        try:
            c = self._conn.cursor()
            c.execute(sql)

            result = c.fetchone()
            #print(result)
            if result is None:
                return None

            user = DiscordUser(result[0], result[1], result[2], result[3], result[4], result[5])

            #print(user)

            return user
        except Error as e:
            print(e)

    def rename_discord_user(self, discord_user_id, new_name):
        # TODO Prevent SQL Injection with name
        try:
            c = self._conn.cursor()
            sql_update_user_name = f"""UPDATE DiscordUsers
            SET CurrentUsername = {new_name}
            WHERE DiscordUserId = {discord_user_id};"""
            c.execute(sql_update_user_name)

            self._conn.commit()

            return self.get_discord_user(discord_user_id)
        except Error as e:
            print(e) 

    def change_credits(self, discord_user_id, transaction_type_id, discord_message_id, discord_channel_id, amount=None, reason=None):

        # TODO Pass with params to prevent injection
        sql = f"""SELECT * FROM SocialCreditTransactionTypes WHERE SocialCreditTransactionTypeId = {transaction_type_id}"""

        try:
            c = self._conn.cursor()
            c.execute(sql)
            result = c.fetchone()


            print(result)  
            
            if result[2] is not None and amount is None:
                amount = int(result[2])

            print(amount)
            
            if result is None:
                print(f"transaction type {transaction_type_id} not found")
                return None

            if amount is None:
                print(f"amount is None")
                return None

         
            sql_update_credits = f"""UPDATE DiscordUsers
            SET SocialCredit = SocialCredit + {amount}
            WHERE DiscordUserId = {discord_user_id};"""
            c.execute(sql_update_credits)


        
            sql_update_credits_history = f"""
            INSERT INTO SocialCreditTransactions 
            (Amount, SocialCreditTransactionTypeId, DiscordUserId, DiscordMessageId, DiscordChannelId, Reason)
            VALUES ({amount}, {transaction_type_id}, {discord_user_id}, {discord_message_id}, {discord_channel_id}, '{reason}');"""
            #print(sql_update_credits_history)

            c.execute(sql_update_credits_history)


            self._conn.commit()

            return self.get_discord_user(discord_user_id)
        except Error as e:
            print(e)

    def create_discord_user(self, discord_user_id, name, social_credit=1000, is_bot=False, is_admin=False):

        # TODO Pass with params to prevent injection
        sql = f"""INSERT INTO DiscordUsers VALUES({discord_user_id}, '{name}', '{name}', {social_credit}, {int(is_bot)}, {int(is_admin)});"""

        try:
            c = self._conn.cursor()
            c.execute(sql)
            self._conn.commit()
            return self.get_discord_user(discord_user_id)
        except Error as e:
            print(e)