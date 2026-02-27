import sys
import types

# --- IMGHDR XATOSINI TUZATISH (PYTHON 3.13+ UCHUN) ---
# Bu blok telegram kutubxonasi qidirayotgan imghdr modulini sun'iy yaratadi
try:
    import imghdr
except ImportError:
    imghdr = types.ModuleType("imghdr")
    imghdr.what = lambda file, h=None: None
    sys.modules["imghdr"] = imghdr
# ----------------------------------------------------

import os
import google.generativeai as genai
from flask import Flask
from threading import Thread
from telegram import Update, Bot, ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# 1. Render uchun server (uyqudan uyg'otish uchun)
app = Flask('')

@app.route('/')
def home():
    return "Bot ishlamoqda!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# 2. KALITLARNI SHU YERGA YOZING
TOKEN = '8236421862:AAE-h3m-RFGvVfl6x8O8Wi5YkKNLVUGGLrw' 
GEMINI_API_KEY = 'AIzaSyBDOUmmNJ89Qh6xziaHnpTDIkMN4g_h1_4'

# Gemini AI sozlamalari
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Salom! Men bepul Gemini AI botiman. Savolingizni yozing!")

def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text
    if not user_message:
        return
    
    # "Yozmoqda..." statusi
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    try:
        response = model.generate_content(user_message)
        update.message.reply_text(response.text)
    except Exception as e:
        print(f"Xato: {e}")
        update.message.reply_text("Kechirasiz, xatolik yuz berdi. API kalitini tekshiring.")

if __name__ == '__main__':
    # Flaskni alohida oqimda yurgizish
    Thread(target=run).start()

    # Telegram botni ishga tushirish
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), handle_message))

    updater.start_polling()
    updater.idle()
    
