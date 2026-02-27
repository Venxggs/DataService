import os
import requests
from flask import Flask
from threading import Thread
from telegram import Update, Bot, ChatAction, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# 1. Render o'chirib qo'ymasligi uchun kichik server (Flask)
app = Flask('')

@app.route('/')
def home():
    return "Bot ishlamoqda!"

def run():
    # Render avtomatik PORT beradi, bo'lmasa 8080 ishlatiladi
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# 2. SOZLAMALAR (Siz bergan kalitlar bilan)
TOKEN = '8236421862:AAHFFqHqv6X5HinHOdGXKndJYQ0dRaUs1BY'
DEEPSEEK_API_KEY = 'sk-1de6581b14634a088eba8d8d2c0039b0'
DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'

dialog_context = {}
current_mode = 'deepseek-chat'

def start(update: Update, context: CallbackContext):
    keyboard = [['/help'], ['/clear'], ['/mode']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)
    update.message.reply_text(
        "Salom! DeepSeek bot tayyor. Savolingizni yuboring!",
        reply_markup=reply_markup
    )

def clear(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    dialog_context[chat_id] = []
    update.message.reply_text("Suhbat tarixi o'chirildi. Yangi savol so'rashingiz mumkin.")

def switch_mode(update: Update, context: CallbackContext):
    global current_mode
    current_mode = 'deepseek-coder' if current_mode == 'deepseek-chat' else 'deepseek-chat'
    update.message.reply_text(f"Hozirgi rejim o'zgardi: **{current_mode}**", parse_mode='Markdown')

def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text
    chat_id = update.effective_chat.id

    if not user_message: return

    # "Yozmoqda..." statusini chiqarish
    context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    # Kontekstni boshqarish
    if chat_id not in dialog_context:
        dialog_context[chat_id] = []
    
    dialog_context[chat_id].append({'role': 'user', 'content': user_message})

    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json'
    }

    data = {
        'model': current_mode,
        'messages': dialog_context[chat_id],
        'temperature': 0.7
    }

    try:
        # APIga so'rov yuborish (timeout 60 soniya)
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        bot_response = response.json()['choices'][0]['message']['content']
        
        # Bot javobini kontekstga qo'shish
        dialog_context[chat_id].append({'role': 'assistant', 'content': bot_response})
        update.message.reply_text(bot_response)
    except Exception as e:
        print(f"Xato: {e}")
        update.message.reply_text("Kechirasiz, DeepSeek ulanishda xato berdi. API kalit faolligini tekshiring.")

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Buyruqlar:\n"
        "/start - Botni qayta ishga tushirish\n"
        "/clear - Suhbat xotirasini tozalash\n"
        "/mode - Chat va Kod yozish rejimini almashtirish"
    )

if __name__ == '__main__':
    # Renderda uxlab qolmasligi uchun Flaskni alohida oqimda yurgizamiz
    Thread(target=run).start()

    # Botni ishga tushirish
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('clear', clear))
    dp.add_handler(CommandHandler('mode', switch_mode))
    dp.add_handler(CommandHandler('help', help_command))
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), handle_message))

    updater.start_polling()
    updater.idle()
  
