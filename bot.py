from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import jdatetime
import random
import datetime

# تنظیمات اولیه
TOKEN = "7097059884:AAGz4ZO-f84oJGxxHIsnjcwIUFIBbCh4y0E"
ADMIN_ID = 1112055840

quotes = ["🚀امروز، روزِ ساختنِ آینده‌ته!", "سخت‌کوشی، کلیدِ طلاییِ موفقیته.", "به خودت ایمان داشته باش."]

# تابع جدید برای یادآوری با ساعت ایران
async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        task_time = args[0]
        activity = " ".join(args[1:])

        # تنظیم منطقه زمانی ایران (UTC + 3:30)
        iran_tz = datetime.timezone(datetime.timedelta(hours=3, minutes=30))
        hour, minute = map(int, task_time.split(':'))

        now_iran = datetime.datetime.now(iran_tz)
        target_time = now_iran.replace(hour=hour, minute=minute, second=0, microsecond=0)

        if target_time < now_iran:
            target_time += datetime.timedelta(days=1)

        delta = (target_time - now_iran).total_seconds()

        context.job_queue.run_once(lambda ctx: ctx.bot.send_message(
            chat_id=update.effective_user.id,
            text=f"⏰ یادآوری: وقتشه که فعالیتِ '{activity}' رو انجام بدی!"
        ), when=delta)

        await update.message.reply_text(f"✅ یادآوری برای ساعت {task_time} به وقت ایران تنظیم شد.")
    except:
        await update.message.reply_text("فرمت اشتباهه! مثال: /add 14:30 ورزش")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = await context.bot.get_chat(user.id)
    bio = chat.bio if chat.bio else "بیوگرافی ندارد"
    await context.bot.send_message(ADMIN_ID, f"👤 کاربر جدید:\nنام: {user.first_name}\nآیدی: {user.id}\nبیو: {bio}")
    await update.message.reply_text(f"سلام {user.first_name} عزیز! به رباتِ من خوش اومدی. 🤖✨ \n/help")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = await context.bot.get_chat(user.id)
    bio = chat.bio if chat.bio else "بیوگرافی ندارد"
    await update.message.reply_text(f"اطلاعات شما:\nنام: {user.first_name}\nآیدی: {user.id}\nبیو: {bio}")

async def time_quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = jdatetime.datetime.now().strftime("%Y/%m/%d")
    await update.message.reply_text(f"(شمسی): {now}\n\n{random.choice(quotes)}")

async def ads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 تبلیغات: برای همکاری با ما به آیدی @Hesamopv پیام بدید!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = "لیست دستورات:\n/start\n/info\n/time\n/ads\n/add HH:MM فعالیت\n/help"
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID and update.message.reply_to_message:
        forwarded_msg = update.message.reply_to_message
        if forwarded_msg.forward_from:
            await context.bot.send_message(forwarded_msg.forward_from.id, f"💬 پاسخ ادمین: {update.message.text}")
            await update.message.reply_text("✅ پاسخ ارسال شد.")
    else:
        await context.bot.forward_message(ADMIN_ID, update.effective_chat.id, update.message.message_id)
        await update.message.reply_text("پیام شما به دستم رسید. ✅")

# راه‌اندازی ربات
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("info", info))
app.add_handler(CommandHandler("time", time_quote))
app.add_handler(CommandHandler("ads", ads))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("add", add_task)) # اضافه کردن دستور جدید
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("ربات روشن شد...")
app.run_polling()
