
import requests
import asyncio
import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ------------------ কনফিগারেশন ------------------
BOT_TOKEN = "8590972749:AAFkOzTeDbp6uxjLHV03y-iZjKcj2CBg2Fk"
API_URL = "http://147.135.212.197/crapi/st/viewstats"
PANEL_TOKEN = "RFdUREJBUzR9T4dVc49ndmFra1NYV5CIhpGVcnaOYmqHhJZXfYGJSQ=="

# ------------------ ফাংশন: ডাটা সংগ্রহ ------------------
def get_all_numbers():
    try:
        params = {"token": PANEL_TOKEN, "records": ""}
        response = requests.get(API_URL, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, list):
            # প্যানেলের লিস্ট থেকে সব ফোন নাম্বার (index 1) বের করা
            # set() ব্যবহার করা হয়েছে যাতে ডুপ্লিকেট নাম্বার না আসে
            numbers = set(entry[1].strip() for entry in data if len(entry) > 1)
            return sorted(list(numbers))
        return []
    except Exception as e:
        print(f"Error fetching API: {e}")
        return None

# ------------------ বট কমান্ডস ------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📁 Get Numbers File", callback_data="get_file")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👋 **স্বাগতম!**\n\nপ্যানেলে থাকা সকল নাম্বার ফাইল আকারে পেতে নিচের বাটনে ক্লিক করুন।",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "get_file":
        await query.edit_message_text("⏳ প্যানেল থেকে নাম্বার সংগ্রহ করা হচ্ছে... দয়া করে অপেক্ষা করুন।")
        
        numbers = get_all_numbers()
        
        if numbers is None:
            await query.edit_message_text("❌ এপিআই কানেকশনে সমস্যা হয়েছে! প্যানেল চেক করুন।")
            return
            
        if not numbers:
            await query.edit_message_text("⚠️ প্যানেলে বর্তমানে কোনো নাম্বার খুঁজে পাওয়া যায়নি।")
            return

        # নাম্বারগুলোকে একটি স্ট্রিং-এ রূপান্তর (প্রতি লাইনে একটি নাম্বার)
        numbers_text = "\n".join(numbers)
        
        # মেমোরিতে ফাইল তৈরি করা (আলাদা করে ফোনে সেভ করার প্রয়োজন নেই)
        file_obj = io.BytesIO(numbers_text.encode('utf-8'))
        file_obj.name = "panel_numbers.txt"
        
        try:
            await query.message.reply_document(
                document=file_obj,
                caption=f"✅ সফলভাবে সব নাম্বার বের করা হয়েছে।\n📊 **মোট ইউনিক নাম্বার:** {len(numbers)}টি",
            )
            await query.edit_message_text("✅ ফাইল পাঠানো সম্পন্ন হয়েছে।")
        except Exception as e:
            await query.edit_message_text(f"❌ ফাইল পাঠাতে সমস্যা হয়েছে: {e}")

# ------------------ মেইন ফাংশন ------------------
if __name__ == "__main__":
    print("🤖 Number Exporter Bot is starting...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()
