import telebot, requests, json, os, time
from telebot import types
from datetime import datetime, timedelta

# --- কনফিগারেশন ---
TOKEN = '8691984492:AAHakoP3nJi1mACTkQi3fjLEOpnlP5_tBq4'
ADMIN_ID = 8682954945 
ADMIN_USER = "@tstohin" 
SETTINGS_FILE = 'settings.json'
DB_FILE = 'members_db.json'

bot = telebot.TeleBot(TOKEN)

# --- ডাটা হ্যান্ডলিং ---
def load_data(file, default):
    if os.path.exists(file):
        try:
            with open(file, 'r') as f: return json.load(f)
        except: return default
    return default

def save_data(file, data):
    with open(file, 'w') as f: json.dump(data, f)

settings = load_data(SETTINGS_FILE, {
    "api_key": "YOUR_API_KEY", 
    "pay_num": "01909242397", 
    "countries": {"🇧🇩 Bangladesh": "19"},
    "all_users": [],
    "service": "wa"
})

members_raw = load_data(DB_FILE, {})
members = {int(k): datetime.fromisoformat(v) for k, v in members_raw.items()}

def save_members():
    data = {str(k): v.isoformat() for k, v in members.items()}
    save_data(DB_FILE, data)

def is_member(user_id):
    if user_id == ADMIN_ID: return True
    if user_id in members:
        if datetime.now() < members[user_id]: return True
        else:
            del members[user_id]
            save_members()
    return False

# --- মেনু সেটআপ ---
def main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton('📲 নম্বর নিন'), types.KeyboardButton('📋 প্রোফাইল'))
    if user_id == ADMIN_ID:
        markup.add(types.KeyboardButton('⚙️ মাস্টার প্যানেল'))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if uid not in settings['all_users']:
        settings['all_users'].append(uid)
        save_data(SETTINGS_FILE, settings)

    welcome_text = (
        f"👋 স্বাগতম **Fast-SMS-Pro** বটে!\n\n"
        f"💰 মেম্বারশিপ ফি: ২০০ টাকা (৩০ দিন)\n"
        f"📱 বিকাশ (Personal): `{settings['pay_num']}`\n"
        f"🆔 আপনার আইডি: `{uid}`\n\n"
        f"👨‍💻 অ্যাডমিন: {ADMIN_USER}"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📩 মেসেজ অ্যাডমিন", url=f"https://t.me/{ADMIN_USER.replace('@','')}"))
    bot.send_message(uid, welcome_text, reply_markup=main_menu(uid), parse_mode="Markdown")

# --- ওটিপি প্রসেসিং ---
def request_number(chat_id, c_code, message_id=None):
    if message_id:
        bot.edit_message_text("⏳ নতুন নম্বর খোঁজা হচ্ছে...", chat_id, message_id)
    else:
        msg = bot.send_message(chat_id, "⏳ নম্বর খোঁজা হচ্ছে...")
        message_id = msg.message_id

    url = f"https://smsbower.page/stubs/handler_api.php?api_key={settings['api_key']}&action=getNumber&service={settings['service']}&country={c_code}"
    try:
        res = requests.get(url).text
        if "ACCESS_NUMBER" in res:
            _, o_id, phone = res.split(':')
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔄 Change Number", callback_data=f"get_{c_code}"))
            bot.edit_message_text(f"✅ নম্বর: `+{phone}`\n🆔 আইডি: `{o_id}`\n🕒 ওটিপি অপেক্ষা...", chat_id, message_id, reply_markup=markup)
            
            for _ in range(30):
                time.sleep(10)
                otp_res = requests.get(f"https://smsbower.page/stubs/handler_api.php?api_key={settings['api_key']}&action=getStatus&id={o_id}").text
                if "STATUS_OK" in otp_res:
                    bot.send_message(chat_id, f"🎯 **OTP: {otp_res.split(':')[1]}**\nনম্বর: `+{phone}`", parse_mode="Markdown")
                    return
        else: bot.edit_message_text(f"❌ প্যানেল এরর: {res}", chat_id, message_id)
    except: bot.edit_message_text("❌ কানেকশন এরর!", chat_id, message_id)

@bot.message_handler(func=lambda m: m.text == '📲 নম্বর নিন')
def get_num(message):
    uid = message.from_user.id
    if is_member(uid):
        markup = types.InlineKeyboardMarkup(row_width=2)
        btns = [types.InlineKeyboardButton(n, callback_data=f"get_{c}") for n, c in settings['countries'].items()]
        markup.add(*btns)
        bot.send_message(uid, "🌍 **একটি দেশ নির্বাচন করুন:**", reply_markup=markup, parse_mode="Markdown")
    else:
        bot.send_message(uid, "❌ আপনার মেম্বারশিপ নেই!")

# --- মাস্টার প্যানেল ---
@bot.message_handler(func=lambda m: m.text == '⚙️ মাস্টার প্যানেল')
def admin_panel(message):
    if message.from_user.id != ADMIN_ID: return
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("➕ মেম্বার অ্যাড", callback_data="adm_add"),
        types.InlineKeyboardButton("👤 মেম্বার রিমুভ", callback_data="adm_rem"),
        types.InlineKeyboardButton("🌍 দেশ যোগ", callback_data="adm_c"),
        types.InlineKeyboardButton("🗑️ দেশ রিমুভ", callback_data="adm_dc"),
        types.InlineKeyboardButton("💳 সেটআপ", callback_data="adm_set"),
        types.InlineKeyboardButton("📢 ব্রডকাস্ট", callback_data="adm_bc")
    )
    bot.send_message(ADMIN_ID, "🛠 **মাস্টার কন্ট্রোল প্যানেল**", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: True)
def process_callbacks(call):
    if call.data.startswith('get_'):
        request_number(call.message.chat.id, call.data.split('_')[1], call.message.message_id)
    elif call.data.startswith('adm_'):
        if call.from_user.id != ADMIN_ID: return
        if call.data == "adm_add":
            m = bot.send_message(ADMIN_ID, "👤 আইডি দিন:")
            bot.register_next_step_handler(m, add_mem)
        elif call.data == "adm_rem":
            m = bot.send_message(ADMIN_ID, "👤 রিমুভ আইডি দিন:")
            bot.register_next_step_handler(m, rem_mem)
        elif call.data == "adm_c":
            m = bot.send_message(ADMIN_ID, "🌍 নাম ও কোড (India:91):")
            bot.register_next_step_handler(m, add_country)
        elif call.data == "adm_dc":
            markup = types.InlineKeyboardMarkup()
            for n in settings['countries']:
                markup.add(types.InlineKeyboardButton(f"❌ {n}", callback_data=f"delc_{n}"))
            bot.send_message(ADMIN_ID, "🗑️ দেশ রিমুভ করুন:", reply_markup=markup)
        elif call.data == "adm_set":
            m = bot.send_message(ADMIN_ID, "🔑 API Key বা বিকাশ নম্বর দিন:")
            bot.register_next_step_handler(m, update_settings)
        elif call.data == "adm_bc":
            m = bot.send_message(ADMIN_ID, "📢 নোটিশ লিখুন:")
            bot.register_next_step_handler(m, broadcast)
    elif call.data.startswith('delc_'):
        c_name = call.data.split('_')[1]
        if c_name in settings['countries']:
            del settings['countries'][c_name]
            save_data(SETTINGS_FILE, settings)
            bot.delete_message(call.message.chat.id, call.message.message_id)

def add_mem(message):
    try:
        target = int(message.text)
        members[target] = datetime.now() + timedelta(days=30)
        save_members()
        bot.reply_to(message, f"✅ {target} সফল।")
    except: bot.send_message(ADMIN_ID, "ভুল আইডি।")

def rem_mem(message):
    try:
        target = int(message.text)
        if target in members:
            del members[target]
            save_members()
            bot.reply_to(message, "✅ রিমুভ সফল।")
    except: pass

def add_country(message):
    try:
        n, c = message.text.split(':')
        settings['countries'][n.strip()] = c.strip()
        save_data(SETTINGS_FILE, settings)
        bot.reply_to(message, "✅ যোগ হয়েছে।")
    except: pass

def update_settings(message):
    text = message.text
    if text.isdigit(): settings['pay_num'] = text
    else: settings['api_key'] = text
    save_data(SETTINGS_FILE, settings)
    bot.reply_to(message, "✅ আপডেট সফল।")

def broadcast(message):
    for u in settings['all_users']:
        try: bot.send_message(u, f"📢 **নোটিশ:**\n\n{message.text}", parse_mode="Markdown")
        except: pass

# অটো রিস্টার্ট লুপ
while True:
    try:
        bot.polling(none_stop=True, timeout=60)
    except:
        time.sleep(10)
