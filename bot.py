from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import jdatetime
import random

# تنظیمات اولیه
TOKEN = "7097059884:AAGz4ZO-f84oJGxxHIsnjcwIUFIBbCh4y0E"
ADMIN_ID = 1112055840

quotes = ["🚀امروز، روزِ ساختنِ آینده‌ته!", "سخت‌کوشی، کلیدِ طلاییِ موفقیته.", "به خودت ایمان داشته باش."]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"سلام {update.effective_user.first_name} عزیز! \n/help به رباتِ من خوش اومدی. 🤖✨")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"اطلاعات شما:\nنام: {user.first_name}\nآیدی: {user.id}")

async def time_quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # دریافت تاریخ و زمان شمسی
    now = jdatetime.datetime.now()
    await update.message.reply_text(f"(شمسی): {now}\n\n{random.choice(quotes)}")

async def ads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 تبلیغات: برای همکاری با ما به آیدی @Hesamopv پیام بدید!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "لیست دستورات ربات: 📋\n\n"
        "/start - شروع کار\n/info - اطلاعات کاربری\n"
        "/time - تاریخ شمسی\n/ads - تبلیغات\n/help - راهنما\n\n"
        "هر پیامی غیر از دستورات بفرستی، ناشناس به دست من می‌رسه! 📩"
    )
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # اگر ادمین روی پیام فوروارد شده ریپلای کرد
    if update.effective_user.id == ADMIN_ID and update.message.reply_to_message:
        forwarded_msg = update.message.reply_to_message
        if forwarded_msg.forward_from:
            user_id = forwarded_msg.forward_from.id
            await context.bot.send_message(chat_id=user_id, text=f"💬 پاسخ ادمین: {update.message.text}")
            await update.message.reply_text("✅ پاسخ با موفقیت ارسال شد.")
    else:
        # فوروارد پیام کاربر به ادمین
        await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=update.effective_chat.id, message_id=update.message.message_id)
        await update.message.reply_text("پیام شما به دستم رسید در اولین فرصت پاسخگوعم. ✅")

# راه‌اندازی ربات
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("info", info))
app.add_handler(CommandHandler("time", time_quote))
app.add_handler(CommandHandler("ads", ads))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("ربات روشن شد...")
app.run_polling()
