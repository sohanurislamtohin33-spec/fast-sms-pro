import telebot
import requests
from telebot import types

# --- নিজের তথ্য দিয়ে নিচের ৪টি ঘর পূরণ করুন ---
API_TOKEN = 'আপনার_বট_টোকেন_এখানে' 
ADMIN_ID = 123456789  # আপনার টেলিগ্রাম আইডি (বট @userinfobot এ পাবেন)
CHANNEL_ID = '@YourChannel' # আপনার চ্যানেলের ইউজারনেম (সহ @ চিহ্ন)
OTP_GROUP_ID = -100XXXXXXXX # আপনার ওটিপি গ্রুপের আইডি

bot = telebot.TeleBot(API_TOKEN)

# ডেটাবেস সেটিংস (বট অফ হলে এটি আগের অবস্থায় ফিরে যাবে, তাই পার্মানেন্ট চাইলে ডাটাবেজ লাগে)
config = {
    "api_key": "আপনার_এপিআই_কি",
    "bkash": "017XXXXXXXX",
    "users": [], # একটিভ মেম্বারদের আইডি থাকবে এখানে
}

# ফোর্স সাবস্ক্রাইব চেক
def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if not is_subscribed(user_id):
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("চ্যানেলে জয়েন করুন", url=f"https://t.me/{CHANNEL_ID[1:]}")
        markup.add(btn)
        bot.send_message(message.chat.id, "❌ আপনি আমাদের চ্যানেলে জয়েন নেই! জয়েন করে আবার /start দিন।", reply_markup=markup)
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📱 Get 3 Numbers", "👤 My Profile")
    markup.add("💳 Membership", "👨‍💻 Admin")
    bot.send_message(message.chat.id, "বটে আপনাকে স্বাগতম! নিচের মেনু ব্যবহার করুন।", reply_markup=markup)

# এডমিন প্যানেল কমান্ড
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("➕ Add User", "➖ Remove User")
        markup.add("💰 Change bKash", "🔑 Update API")
        markup.add("🔙 Back to Menu")
        bot.send_message(message.chat.id, "🛠 এডমিন কন্ট্রোল প্যানেল:", reply_markup=markup)

# ইউজার অ্যাড করার লজিক (উদাহরণ)
@bot.message_handler(func=lambda message: message.text == "➕ Add User" and message.from_user.id == ADMIN_ID)
def add_user_prompt(message):
    msg = bot.send_message(message.chat.id, "যাকে অ্যাড করতে চান তার User ID দিন:")
    bot.register_next_step_handler(msg, save_user)

def save_user(message):
    config["users"].append(int(message.text))
    bot.send_message(message.chat.id, f"✅ ইউজার {message.text} এখন মেম্বারশিপ পেয়েছে!")

# নাম্বার পাওয়ার লজিক
@bot.message_handler(func=lambda message: message.text == "📱 Get 3 Numbers")
def send_numbers(message):
    if message.from_user.id not in config["users"] and message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, f"⚠️ আপনার মেম্বারশিপ নেই। বিকাশ করুন: {config['bkash']}")
        return
    
    # এখানে আপনার API দিয়ে নাম্বার কল করার কোড হবে
    numbers = ["+88017XXX1", "+88017XXX2", "+88017XXX3"]
    text = "✅ আপনার ৩টি নাম্বার:\n" + "\n".join(numbers)
    bot.send_message(message.chat.id, text)

bot.polling(none_stop=True)
