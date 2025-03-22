import telebot
import sqlite3
from datetime import datetime

TOKEN = "7227494015:AAGoDW40q5pEGMSz9qF4iQUZ9OeVnoYijro"
ADMIN_ID = 6237565889

bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_join TIMESTAMP
    )
""")
conn.commit()

def generate_code(user_id):
    last_four_digits = str(user_id)[-4:]
    reversed_code = last_four_digits[::-1]
    return reversed_code

def escape_markdown(text):
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    username = escape_markdown(message.from_user.first_name)
    code = generate_code(user_id)
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M")

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user_exists = cursor.fetchone()

    if not user_exists:
        cursor.execute("INSERT INTO users (user_id, username, first_join) VALUES (?, ?, ?)", 
                       (user_id, username, time_now))
        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]

        admin_message = (
            f"📢 مستخدم جديد دخل البوت\n"
            f"👤 الاسم: {username}\n"
            f"🆔 ID: `{user_id}`\n"
            f"⏰ الوقت: {escape_markdown(time_now)}\n"
            f"📊 إجمالي المستخدمين: {user_count}"
        )
        bot.send_message(ADMIN_ID, admin_message, parse_mode="MarkdownV2")

    bot.reply_to(message, f"Your verification code is:\n`{code}`", parse_mode="MarkdownV2")

@bot.message_handler(commands=['voidxman'])
def send_stats(message):
    if message.chat.id == ADMIN_ID:
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        bot.reply_to(message, f"📊 إجمالي عدد المستخدمين: {user_count}")
    else:
        bot.reply_to(message, "❌ لا يمكنك استخدام هذا الأمر.")

bot.polling()
