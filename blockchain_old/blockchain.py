import disnake
from disnake.ext import commands
import hashlib
import time
import json
import sqlite3
import os


class Block:
    def __init__(self, index, previous_hash, timestamp, data):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        value = str(self.index) + str(self.previous_hash) + str(self.timestamp) + str(self.data)
        return hashlib.sha256(value.encode()).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = self.load_chain()
        self.smart_contract = SmartContract(self)

    def create_genesis_block(self):
        return Block(0, "0", time.time(), "Genesis Block")

    def add_block(self, sender, transaction, recipient_username, amount):
        index = len(self.chain)
        previous_block = self.chain[-1]
        timestamp = time.time()
        new_block = Block(index, previous_block.hash, timestamp, transaction)
        self.chain.append(new_block)

        sender_username = self.smart_contract.get_username(sender)
        self.smart_contract.add_transaction(sender, sender_username, None, recipient_username, amount)
        self.save_chain()

    def get_all_transactions(self):
        transactions = []
        for block in self.chain:
            transactions.append(block.data)
        return transactions

    def save_chain(self):
        with open("blockchain.json", "w") as f:
            serialized_chain = [block.__dict__ for block in self.chain]
            json.dump(serialized_chain, f)

    def load_chain(self):
        try:
            with open("blockchain.json", "r") as f:
                serialized_chain = json.load(f)
                return [Block(index=block['index'],
                              previous_hash=block['previous_hash'],
                              timestamp=block['timestamp'],
                              data=block['data']) for block in serialized_chain]
        except FileNotFoundError:
            return [self.create_genesis_block()]


class SmartContract:
    def __init__(self, blockchain):
        self.blockchain = blockchain
        self.conn = sqlite3.connect("balances.db")
        self.cursor = self.conn.cursor()
        self.initialize_database()

    def initialize_database(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS balances (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                balance INTEGER DEFAULT 100
            )
        ''')
        self.conn.commit()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER,
                sender_username TEXT,
                recipient_id INTEGER,
                recipient_username TEXT,
                amount INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES balances(user_id),
                FOREIGN KEY (recipient_id) REFERENCES balances(user_id)
            )
        ''')
        self.conn.commit()

    def process_transaction(self, sender, recipient, amount):
        sender_balance = self.get_balance(sender)
        sender_username = self.get_username(sender)

        if sender_balance < amount:
            return False

        recipient_username = self.get_username(recipient)

        self.blockchain.add_block(sender, f"{sender_username} sent {amount} to {recipient_username}", recipient_username, amount)

        self.update_balance(sender, sender_username, sender_balance - amount)
        self.update_balance(recipient, recipient_username, self.get_balance(recipient) + amount)

        return True

    def add_transaction(self, sender, sender_username, recipient, recipient_username, amount):
        self.cursor.execute("""
            INSERT INTO transactions (sender_id, sender_username, recipient_id, recipient_username, amount) VALUES (?, ?, ?, ?, ?)
        """, (sender, sender_username, recipient, recipient_username, amount))
        self.conn.commit()

    def get_balance(self, user_id):
        self.cursor.execute("SELECT balance FROM balances WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def update_balance(self, user_id, username, new_balance):
        self.cursor.execute("""
            INSERT OR REPLACE INTO balances (user_id, username, balance) VALUES (?, ?, ?)
        """, (user_id, username, new_balance))
        self.conn.commit()

    def get_all_transactions(self):
        self.cursor.execute("""
            SELECT sender_id, recipient_username, amount, timestamp FROM transactions
        """)
        transactions = self.cursor.fetchall()

        formatted_transactions = [
            f"{self.get_username(sender)} sent {amount} to {self.get_username(recipient)} at {timestamp}"
            for sender, recipient, amount, timestamp in transactions
        ]

        return formatted_transactions

    def get_username(self, user_id):
        self.cursor.execute("SELECT username FROM balances WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def register_user(self, user_id, username):
        self.cursor.execute("""
            INSERT INTO balances (user_id, username) VALUES (?, ?)
        """, (user_id, username))
        self.conn.commit()

class BlockchainCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.blockchain = Blockchain()
        self.smart_contract = SmartContract(self.blockchain)

    @commands.slash_command()
    async def send_transaction(self, ctx, recipient: disnake.User, amount: int):
        sender = ctx.author.id

        sender_username = self.smart_contract.get_username(sender)
        if sender_username is None:
            await ctx.send("Вы не зарегистрированы. Используйте команду /register (username) чтобы зарегистрироваться.")
            return

        recipient_username = self.smart_contract.get_username(recipient.id)
        if recipient_username is None:
            await ctx.send(f"Пользователь с ID {recipient.id} не зарегистрирован.")
            return

        success = self.smart_contract.process_transaction(sender, recipient.id, amount)

        if success:
            await ctx.send(f"Транзакция успешно прошла! Пользователь {sender_username} отправил {amount} пользователю {recipient_username}")
        else:
            await ctx.send("Транзакция не удалась.")

    @commands.slash_command()
    async def get_transactions(self, ctx):
        transactions = self.smart_contract.get_all_transactions()
        if transactions:
            await ctx.send("\n".join(transactions))
        else:
            await ctx.send("No transactions found.")

    @commands.slash_command()
    async def register(self, ctx, username: str):
        user_id = ctx.author.id
        success = self.smart_contract.register_user(user_id, username)

        if success:
            await ctx.send(f"Пользователь {username} успешно создан! У вас на балансе 100 монет.")
        else:
            await ctx.send(f"Регистрация не удалась. Пользователь {username} уже существует.")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'BlockchainCog is ready!')


def setup(bot):
    bot.add_cog(BlockchainCog(bot))
