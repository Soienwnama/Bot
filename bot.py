import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher.filters import Command

API_TOKEN = "8106606314:AAGZTkzoGQnXPaF_vc3MyHJIaLu4xpiHW2Y"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        balance INTEGER DEFAULT 0
    )
""")
conn.commit()

def get_balance(user_id):
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    return user[0] if user else 0

def add_balance(user_id, amount):
    cursor.execute("INSERT INTO users (user_id, balance) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET balance = balance + ?", (user_id, amount, amount))
    conn.commit()

def set_balance(user_id, amount):
    cursor.execute("INSERT INTO users (user_id, balance) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET balance = ?", (user_id, amount, amount))
    conn.commit()

@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, 0)", (user_id,))
    conn.commit()
    
    await message.reply("Welcome to Vstock! Use /balance to check your balance.")

@dp.message_handler(commands=["balance"])
async def check_balance(message: types.Message):
    user_id = message.from_user.id
    balance = get_balance(user_id)
    await message.reply(f"Your balance is: {balance} coins")

@dp.message_handler(commands=["addbalance"])
async def admin_add_balance(message: types.Message):
    admin_id = 5252611252  # Replace with your Telegram ID
    if message.from_user.id != admin_id:
        await message.reply("You are not authorized to use this command.")
        return
    
    args = message.text.split()
    if len(args) != 3:
        await message.reply("Usage: /addbalance user_id amount")
        return
    
    try:
        user_id = int(args[1])
        amount = int(args[2])
        add_balance(user_id, amount)
        await message.reply(f"Added {amount} coins to user {user_id}.")
    except ValueError:
        await message.reply("Invalid user ID or amount.")

@dp.message_handler(commands=["id"])
async def send_user_id(message: types.Message):
    await message.reply(f"Your user ID is: {message.from_user.id}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)