import os
import telebot

# စနစ် (System) ထဲမှာ ဝှက်ထားမယ့် TG_TOKEN ကို လှမ်းဖတ်ခိုင်းတာပါ
BOT_TOKEN = os.environ.get('TG_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# Bot ထဲမှာ /start လို့ နှိပ်ရင် စာပြန်မယ့် ကုဒ်
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "မင်္ဂလာပါဗျာ၊ ကျွန်တော့်ကို ၂၄ နာရီပတ်လုံး သုံးလို့ရပါပြီ။")

bot.infinity_polling()
