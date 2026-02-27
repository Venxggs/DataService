import os
import google.generativeai as genai
from flask import Flask
from threading import Thread
from telegram import Update, Bot, ChatAction, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# 1. Flask server
app = Flask('')
@app.route('/')
def home(): return "Bot ishlamoqda!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# 2. SOZLAMALAR
TELEGRAM_TOKEN = ''
GEMINI_API_KEY = ''

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Salom! Men bepul Gemini AI botiman. Savolingizni yozing!")

def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text
    if not user_message: return

    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    try:
        response = model.generate_content(user_message)
        update.message.reply_text(response.text)
    except Exception as e:
        print(f"Xato: {e}")
        update.message.reply_text("Xatolik yuz berdi. Keyinroq urunib ko'ring.")

if __name__ == '__main__':
    Thread(target=run).start()
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), handle_message))
    updater.start_polling()
    updater.idle()
    
