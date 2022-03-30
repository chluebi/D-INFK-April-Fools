from inspect import trace
import sqlite3
from sqlite3 import Error
import traceback
import discord

from discord_user import DiscordUser
from transaction import Transaction

from events import score_update

from constants import TransactionType
import io
import os
from datetime import datetime

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class SQLiteDBManager(object, metaclass=Singleton):

    def __init__(self, path=None, backup_path=None):
        self._path = path
        self._backup_path = backup_path

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
            self.insert_transaction_types()
            self.insert_key_values()
        except:
            print("---- Error connecting to the database")

    def __del__(self):
        try:
            self._conn.commit()
            self._conn.close()
        except:
            print("---- Error closing database")

        return

    #region Setup DB
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
                                    SocialCreditTransactionTypeId INTEGER NOT NULL,
                                    DiscordUserId INTEGER NOT NULL,
                                    Amount INTEGER NOT NULL,
                                    DateTime TEXT NOT NULL,
                                    DiscordMessageId INTEGER NULL,
                                    DiscordChannelId INTEGER NULL,
                                    Reason TEXT NULL,
                                    FromDiscordUserId INTEGER NULL,
                                    FOREIGN KEY (DiscordUserId) REFERENCES DiscordUsers (DiscordUserId),
                                    FOREIGN KEY (FromDiscordUserId) REFERENCES DiscordUsers (DiscordUserId),
                                    FOREIGN KEY (SocialCreditTransactionTypeId) REFERENCES SocialCreditTransactionTypes (SocialCreditTransactionId)
                                );""")

        sql_queries.append("""CREATE TABLE IF NOT EXISTS StoreKeyValuePairs (
                                    Key TEXT UNIQUE,
                                    Value TEXT NOT NULL,
                                    Type TEXT NOT NULL
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
        (4, 'BirthdayWish', 20, 1),
        (5, 'TAApproved', 5, 1),
        (6, 'ReceiveGoodRep', 20, 1),
        (7, 'InvalidNameChange', -20, 1),
        (8, 'PlayGames', -1, 1),
        (9, 'Mention1984', -20, 1),
        (10, 'Profanity', -10, 0),
        (11, 'RevertTransaction', 0, 0),
        (12, 'JudgeChange', 0, 0),
        (13, 'TimeOut', 250, 0),
        (14, 'EscapeAttempt', -100, 0),
        (15, 'Emotions', -5, 0),
        (16, 'StaffApproved', 10, 0)"""

        try:
            c = self._conn.cursor()
            c.execute(sql)
            self._conn.commit()
        except Error as e:
            print(e)
    #endregion

    #region KeyValue
    def list_keys(self):
        output = ""
        try:
            c = self._conn.cursor()
            c.execute("SELECT * FROM StoreKeyValuePairs")
            
            results = c.fetchall()

            for result in results:
                output = output + str(result) + "\r\n"

            return output
        except Error as e:
            print(e)
        return None

    def insert_key(self, key, value, type):
        # If key exists then update
        if self.key_exists(key):
            return self.update_key(key, value, type)

        try:
            c = self._conn.cursor()
            c.execute("INSERT INTO StoreKeyValuePairs VALUES (?,?,?)", [key, value, type])
            self._conn.commit()

            return self.get_key(key)
        except Error as e:
            print(e)
        return None
    
    def key_exists(self, key):
        return self.get_key(key) is not None

    def get_key(self, key):
        try:
            c = self._conn.cursor()
            c.execute("SELECT * FROM StoreKeyValuePairs WHERE Key = ?", [key])
            
            result = c.fetchone()
            if result is None:
                return None

            typeVal = result[2]
            if typeVal == "str":
                return result[1]
            elif typeVal == "int":
                return int(result[1])
            elif typeVal == "bool":
                return eval(result[1])

            return result
        except Error as e:
            print(e)
            traceback.print_stack()
        return None

    def update_key(self, key, value, type=None):   
        # If key doesnt exists then insert
        if not self.key_exists(key):
            if type is None:
                return None

            return self.insert_key(key, value, type)

        try:
            c = self._conn.cursor()

            if type is None:
                c.execute("UPDATE StoreKeyValuePairs SET Value = ? WHERE Key = ?", [value, key])
            else:
                c.execute("UPDATE StoreKeyValuePairs SET Value = ?, Type = ? WHERE Key = ?", [value, type, key])

            self._conn.commit()
            
            return self.get_key(key)
        except Error as e:
            print(e)
            traceback.print_stack()
        return None
    
    def delete_key(self, key):
        # If Key doesnt exists then dont do anything
        if not self.key_exists(key):
            return False

        try:
            c = self._conn.cursor()
            c.execute("DELETE FROM WHERE Key = ?", [key])
            self._conn.commit()

            return True
        except Error as e:
            print(e)
        
        return False

    def insert_key_values(self):
        sql = f"""
        INSERT INTO StoreKeyValuePairs
        VALUES 
        ('RemovePointsOnRename', 'False', 'bool'),
        ('DiscordServerId', 954423559600631829, 'int'),
        ('ChangelogChannelId', 954423559600631832, 'int'),
        ('ScoreNameChange', 'False', 'bool')"""

        try:
            c = self._conn.cursor()
            c.execute(sql)
            self._conn.commit()
        except Error as e:
            print(e)
    #endregion

    #region Backup
    def progress(self, status, remaining, total):
        # TODO Send to log?
        print(f'Copied {total-remaining} of {total} pages...')
        
    def backup_db(self):
        try:
            now = datetime.now()
            now_string = now.strftime("%Y_%m_%d_%H_%M_%S")
            
            print(self._backup_path)
            if not os.path.exists(self._backup_path):
                os.makedirs(self._backup_path)

            with io.open(os.path.join(self._backup_path, str('backup_' + now_string + '.sql')), 'w') as p: 
                for line in self._conn.iterdump(): 
                    p.write('%s\n' % line)

            self._conn.commit()

            bck = sqlite3.connect(os.path.join(self._backup_path, str('backup_' + now_string + '.db')))
            with bck:
                self._conn.backup(bck, pages=1, progress=self.progress)
            
            bck.close()

            print('Backup performed successfully!')
        except Exception as e:
            print(e)
            traceback.print_stack
    #endregion

    #region SQL
    def sql_query(self, query):
        output = ""
        print(query)
        if query == "backup":
            self.backup_db()
            return "Backup created"

        try:
            c = self._conn.cursor()
            c.execute(query)

            results = c.fetchmany(50)
            names = list(map(lambda x: x[0], c.description))

            output = "``"

            # Header
            for name in names:
                output += name + "\t" 

            output += "``" + "\r\n"

            for result in results:
                output += str(result) + "\r\n"

            return output
        except Error as e:
            print(e)
    #endregion

    #region Transactions
    def get_transaction_by_id(self, transaction_id):
        sql = f"""
        SELECT 
            SocialCreditTransactionId,
            SocialCreditTransactionTypeId,
            DiscordUserId,
            Amount,
            DateTime,
            DiscordMessageId,
            DiscordChannelId,
            Reason,
            FromDiscordUserId
        FROM SocialCreditTransactions WHERE SocialCreditTransactionId = {transaction_id}"""

        try:
            c = self._conn.cursor()
            c.execute(sql)
            result = c.fetchone()
            if result is None:
                return None

            return Transaction(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8])
        except Error as e:
            print(e)

    def get_last_transactions(self, discord_user_id, amount=25):
        transactions = []

        sql = f"""
        SELECT 
            SocialCreditTransactionId,
            SocialCreditTransactionTypeId,
            DiscordUserId,
            Amount,
            DateTime,
            DiscordMessageId,
            DiscordChannelId,
            Reason,
            FromDiscordUserId
        FROM SocialCreditTransactions WHERE DiscordUserId = {discord_user_id} ORDER BY DateTime DESC LIMIT {amount}"""

        try:
            c = self._conn.cursor()
            c.execute(sql)
            results = c.fetchmany(amount)
            if results is None:
                return None

            for result in results:
                transactions.append(Transaction(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8]))

            return transactions
        except Error as e:
            print(e)
    #endregion

    #region Users  
    def get_top_discord_users(self, amount = 10):
        users = []
        sql = f"""SELECT 
            DiscordUserId,
            OldUsername,
            CurrentUsername,
            SocialCredit,
            IsBot,
            IsAdmin 
        FROM DiscordUsers ORDER BY SocialCredit DESC LIMIT {amount}"""

        try:
            c = self._conn.cursor()
            c.execute(sql)

            results = c.fetchmany(amount)
            if results is None:
                return None

            for result in results:
                users.append(DiscordUser(result[0], result[1], result[2], result[3], result[4], result[5]))

            return users
        except Error as e:
            print(e)
        return

    def get_discord_user(self, discord_user_id: int):
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
            if result is None:
                return None

            user = DiscordUser(result[0], result[1], result[2], result[3], result[4], result[5])
            return user
        except Error as e:
            print(e)

    def create_discord_user(self, discord_user_id, name, social_credit=1000, is_bot=False, is_admin=False):
        try:
            c = self._conn.cursor()
            c.execute("""
            INSERT INTO DiscordUsers 
            VALUES(?, ?, ?, ?, ?, ?);""", 
            (discord_user_id, name, name, social_credit, int(is_bot), int(is_admin)))
            self._conn.commit()
            return self.get_discord_user(discord_user_id)
        except Error as e:
            print(e)
            
    def rename_discord_user(self, discord_user_id, new_name):
        try:
            c = self._conn.cursor()
            c.execute("""UPDATE DiscordUsers
            SET CurrentUsername = ?
            WHERE DiscordUserId = ?;""", (new_name, discord_user_id))

            self._conn.commit()
            return self.get_discord_user(discord_user_id)
        except Error as e:
            print(e) 
    #endregion

    #region Credits
    async def change_credits(self, member: discord.Member, transaction_type: TransactionType, from_discord_user_id = None, discord_message_id=None, discord_channel_id=None, amount=None, reason=None):
        discord_user_id = member.id
        transaction_type_id = transaction_type.value


        try:
            c = self._conn.cursor()
            c.execute("SELECT * FROM SocialCreditTransactionTypes WHERE SocialCreditTransactionTypeId = ?", (transaction_type_id, ))
            result = c.fetchone()

            # If no amount is provided take the default for this type
            if result[2] is not None and amount is None:
                amount = int(result[2])
            
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

            c.execute("""
            INSERT INTO SocialCreditTransactions 
            (Amount, SocialCreditTransactionTypeId, DateTime, DiscordUserId, FromDiscordUserId, DiscordMessageId, DiscordChannelId, Reason)
            VALUES (?, ?, datetime(), ?, ?, ?, ?, ?);""", (amount, transaction_type_id, discord_user_id, from_discord_user_id, discord_message_id, discord_channel_id, reason))

            self._conn.commit()
            
            # If reason is not provided use the name of the type
            if reason is None:
                reason = result[1]
            
            user = self.get_discord_user(discord_user_id)
            await score_update(member, user, amount, reason)
            
            return user
        except Error as e:
            print(e)
    #endregion
