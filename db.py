import sqlite3
from sqlite3 import Error

class DiscordUser(object):

    def __init__(self, discord_user_id, old_name, current_name, social_credit, is_bot, is_admin):
        self.discord_user_id = discord_user_id
        self.old_name = old_name
        self.current_name = current_name
        self.social_credit = social_credit
        self.is_bot = is_bot
        self.is_admin = is_admin


    

class SQLiteDBManager(object):

    def __init__(self, path=None):
        self._path = path

        self.dbON = False 
        self._conn = None
        self._c = None

        try:
            db_fname = self._path
            print("---- Connecting to {}".format(db_fname))
            self._conn = sqlite3.connect(db_fname)
            self._c = self._conn.cursor()
            self.dbON = True

            self.initalize_tables()
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
                                        UsernameOld TEXT NOT NULL,
                                        UsernameCurrent TEXT NOT NULL,
                                        SocialCredit INTEGER NULL,
                                        IsBot INTEGER NOT NULL,
                                        IsAdmin INTEGER NOT NULL DEFAULT 0
                                    ); """)

        sql_queries.append(""" CREATE TABLE IF NOT EXISTS SocialCreditTransactionTypes (
                                        SocialCreditTransactionTypeId INT UNIQUE,
                                        Name TEXT NOT NULL,
                                        DefaultAmount INTEGER NULL
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


    def get_discord_user(self, discord_user_id):

        sql = f"""SELECT 
            DiscordUserId,
            UsernameOld,
            UsernameCurrent,
            SocialCredit,
            IsBot,
            IsAdmin 
        FROM DiscordUsers WHERE DiscordUserId = {discord_user_id}"""

        try:
            c = self._conn.cursor()
            c.execute(sql)

            result = c.fetchone()
            print(result)
            if result is None:
                return None

            user = DiscordUser(result[0], result[1], result[2], result[3], result[4], result[5])

            print(user)

            return user
        except Error as e:
            print(e)

        

    def create_discord_user(self, discord_user_id, old_name, current_name, social_credit=1000, is_bot=False, is_admin=False):

        # TODO Pass with params to prevent injection
        sql = f"""INSERT INTO DiscordUsers VALUES({discord_user_id}, '{old_name}', '{current_name}', {social_credit}, {int(is_bot)}, {int(is_admin)});"""

        try:
            c = self._conn.cursor()
            c.execute(sql)
            self._conn.commit()
        except Error as e:
            print(e)