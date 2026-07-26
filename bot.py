from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import datetime
import random

# تنظیمات اولیه
TOKEN = "YOUR_TOKEN"
ADMIN_ID = 123456789  # آیدی عددی خودت رو اینجا وارد کن

quotes = ["امروز، روزِ ساختنِ آینده‌ته!", "سخت‌کوشی، کلیدِ طلاییِ موفقیته.", "به خودت ایمان داشته باش."]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"سلام {update.effective_user.first_name} عزیز! به رباتِ من خوش اومدی. برای دیدن دستورات از /help استفاده کن. 🤖✨")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"اطلاعات شما:\nنام: {user.first_name}\nآیدی: {user.id}")

async def time_quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await update.message.reply_text(f"زمان: {now}\n\n{random.choice(quotes)}")

async def ads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 تبلیغات: برای همکاری با ما به آیدی @YourID پیام بدید!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "لیست دستورات ربات: 📋\n\n"
        "/start - شروع کار\n/info - اطلاعات کاربری\n"
        "/time - زمان و جمله انگیزشی\n/ads - تبلیغات\n/help - راهنما\n\n"
        "هر پیامی غیر از دستورات بفرستی، ناشناس به دست من می‌رسه! 📩"
    )
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # فوروارد پیام کاربر به ادمین
    await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=update.effective_chat.id, message_id=update.message.message_id)
    await update.message.reply_text("پیام شما به دست صاحب ربات رسید. ✅")

# راه‌اندازی ربات
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("info", info))
app.add_handler(CommandHandler("time", time_quote))
app.add_handler(CommandHandler("ads", ads))
app.add_handler(CommandHandler("help", help_command))
# هندلر برای پیام‌های متنی (غیر از دستورات)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("ربات روشن شد...")
app.run_polling()
