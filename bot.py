import telebot

bot = telebot.TeleBot("7097059884:AAGz4ZO-f84oJGxxHIsnjcwIUFIBbCh4y0E")

@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    bot.reply_to(message, f"سلام {name}! 👋\nرباتت فعاله 🎉")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    text = """
🤖 دستورات:
/start - شروع
/help - راهنما
/about - درباره
"""
    bot.reply_to(message, text)

@bot.message_handler(commands=['about'])
def about(message):
    bot.reply_to(message, "این ربات با پایتون ساخته شده 🐍")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, "دستور ناشناس 🤷\n/help رو بزن")

print("🤖 ربات روشن شد")
bot.polling()
