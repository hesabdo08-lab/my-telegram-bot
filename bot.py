from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters, ContextTypes
)
import jdatetime
import random
import datetime

# تنظیمات اولیه
TOKEN = "7097059884:AAGz4ZO-f84oJGxxHIsnjcwIUFIBbCh4y0E"
ADMIN_ID = 1112055840

quotes = ["🚀امروز، روزِ ساختنِ آینده‌ته!", "سخت‌کوشی، کلیدِ طلاییِ موفقیته.", "به خودت ایمان داشته باش."]

IRAN_TZ = datetime.timezone(datetime.timedelta(hours=3, minutes=30))

# مراحل مکالمه‌ی /add
ASK_TIME, ASK_ACTIVITY, CONFIRM = range(3)


# ---------------------------------------------------------
# مکالمه‌ی /add: ساعت -> فعالیت -> تایید
# ---------------------------------------------------------
async def add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ساعت مورد نظر رو به فرمت HH:MM بفرست (مثلاً 14:30):")
    return ASK_TIME


async def add_get_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task_time = update.message.text.strip()
    try:
        hour, minute = map(int, task_time.split(':'))
        if not (0 <= hour < 24 and 0 <= minute < 60):
            raise ValueError
    except ValueError:
        await update.message.reply_text("فرمت درست نیست! دوباره به شکل HH:MM بفرست (مثلاً 14:30):")
        return ASK_TIME

    context.user_data['task_time'] = f"{hour:02d}:{minute:02d}"
    await update.message.reply_text("اسم فعالیت رو بفرست:")
    return ASK_ACTIVITY


async def add_get_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    activity = update.message.text.strip()
    context.user_data['activity'] = activity
    task_time = context.user_data['task_time']

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ تایید", callback_data="add_confirm"),
        InlineKeyboardButton("❌ لغو", callback_data="add_cancel"),
    ]])
    await update.message.reply_text(
        f"ساعت: {task_time}\nفعالیت: {activity}\n\nاطلاعات درسته؟",
        reply_markup=keyboard
    )
    return CONFIRM


async def add_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "add_cancel":
        context.user_data.clear()
        await query.edit_message_text("❌ لغو شد.")
        return ConversationHandler.END

    task_time = context.user_data['task_time']
    activity = context.user_data['activity']
    hour, minute = map(int, task_time.split(':'))
    chat_id = query.from_user.id

    now_iran = datetime.datetime.now(IRAN_TZ)
    target_time = now_iran.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target_time < now_iran:
        target_time += datetime.timedelta(days=1)
    delta = (target_time - now_iran).total_seconds()

    async def send_reminder(ctx: ContextTypes.DEFAULT_TYPE):
        await ctx.bot.send_message(
            chat_id=ctx.job.chat_id,
            text=f"⏰ یادآوری: وقتشه که فعالیتِ '{ctx.job.data}' رو انجام بدی!"
        )

    context.job_queue.run_once(send_reminder, when=delta, chat_id=chat_id, data=activity)

    await query.edit_message_text(f"✅ یادآوری برای ساعت {task_time} (به وقت ایران) ثبت شد.")
    context.user_data.clear()
    return ConversationHandler.END


async def add_cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ عملیات لغو شد.")
    return ConversationHandler.END


# ---------------------------------------------------------
# سایر دستورات
# ---------------------------------------------------------
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
    help_text = (
        "لیست دستورات:\n"
        "/start\n/info\n/time\n/ads\n/add\n/help\n\n"
        "/add: اول ازت ساعت رو می‌پرسه، بعد فعالیت رو، و در آخر با یه دکمه تایید مطمئن می‌شه."
    )
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


# ---------------------------------------------------------
# راه‌اندازی ربات
# ---------------------------------------------------------
app = Application.builder().token(TOKEN).build()

add_conversation = ConversationHandler(
    entry_points=[CommandHandler("add", add_start)],
    states={
        ASK_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_get_time)],
        ASK_ACTIVITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_get_activity)],
        CONFIRM: [CallbackQueryHandler(add_confirm, pattern="^add_(confirm|cancel)$")],
    },
    fallbacks=[CommandHandler("cancel", add_cancel_command)],
)

app.add_handler(add_conversation)
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("info", info))
app.add_handler(CommandHandler("time", time_quote))
app.add_handler(CommandHandler("ads", ads))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("ربات روشن شد...")
app.run_polling()
