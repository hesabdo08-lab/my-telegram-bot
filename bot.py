from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters, ContextTypes
)
import jdatetime
import random
import datetime
import asyncio

# تنظیمات اولیه
TOKEN = "7097059884:AAGz4ZO-f84oJGxxHIsnjcwIUFIBbCh4y0E"
ADMIN_ID = 1112055840

quotes = ["🚀امروز، روزِ ساختنِ آینده‌ته!😉", "سخت‌کوشی، کلیدِ طلاییِ موفقیته✨.", "به خودت ایمان داشته باش."]

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
    user = query.from_user
    chat_id = user.id

    try:
        now_iran = datetime.datetime.now(IRAN_TZ)
        target_time = now_iran.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target_time < now_iran:
            target_time += datetime.timedelta(days=1)
        delta = (target_time - now_iran).total_seconds()

        async def send_reminder_later(bot, delay, cid, act):
            await asyncio.sleep(delay)
            await bot.send_message(
                chat_id=cid,
                text=f"⏰ یادآوری: وقتشه که فعالیتِ '{act}' رو انجام بدی!"
            )

        context.application.create_task(
            send_reminder_later(context.bot, delta, chat_id, activity)
        )

        await query.edit_message_text(f"✅ یادآوری برای ساعت {task_time} (به وقت ایران) ثبت شد.")

        await context.bot.send_message(
            ADMIN_ID,
            f"🔔 یادآوری جدید ثبت شد:\n"
            f"کاربر: {user.first_name} (آیدی: {user.id})\n"
            f"ساعت: {task_time}\n"
            f"فعالیت: {activity}"
        )
    except Exception as e:
        await query.edit_message_text(f"❌ خطا در ثبت یادآوری: {e}")

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
    await update.message.reply_text(
        f"سلام {user.first_name} عزیز! به رباتِ من خوش اومدی. 🤖✨ \n را بزنید /help برای دیدن لیست دستورات گزینه\n\n"
        "✅👇🏽:هر وقت خواستی می‌تونی همینجا برام پیام بفرستی، مستقیم به دستم می‌رسه."
    )


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
        "/start - شروع ربات\n"
        "/info - اطلاعات کاربر\n"
        "/time - تاریخ و جمله انگیزشی\n"
        "/ads - تبلیغات\n"
        "/add - الارم فعالیت\n"
        "/reply - ارسال پیام مستقیم به یک کاربر (فقط ادمین)\n"
        "/help - راهنما\n\n"
        "هر وقت خواستی می‌تونی همینجا برام پیام بفرستی، مستقیم به دستم می‌رسه."
    )
    await update.message.reply_text(help_text)


# ---------------------------------------------------------
# دستور جدید: /reply <user_id> <متن>  (فقط برای ادمین)
# ---------------------------------------------------------
async def reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return  # فقط ادمین اجازه‌ی استفاده داره

    if len(context.args) < 2:
        await update.message.reply_text(
            "استفاده‌ی صحیح:\n/reply <آیدی کاربر> <متن پیام>\n\nمثال:\n/reply 123456789 سلام، چطور می‌تونم کمکتون کنم؟"
        )
        return

    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("آیدی کاربر باید عدد باشه.")
        return

    message_text = " ".join(context.args[1:])

    try:
        await context.bot.send_message(target_id, f"💬 پاسخ ادمین: {message_text}")
        await update.message.reply_text("✅ پیام ارسال شد.")
    except Exception as e:
        await update.message.reply_text(f"❌ ارسال نشد: {e}")


# ---------------------------------------------------------
# فوروارد پیام کاربر به ادمین + پاسخ ادمین با ریپلای
# ---------------------------------------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # اگر ادمین داره روی یک پیامِ فوروارد شده ریپلای می‌کنه
    if update.effective_user.id == ADMIN_ID and update.message.reply_to_message:
        replied = update.message.reply_to_message
        user_map = context.bot_data.get("user_map", {})
        target_id = user_map.get(replied.message_id)

        if target_id is None and replied.forward_from:
            # اگر به هر دلیلی توی نگاشت نبود ولی forward_from موجود بود
            target_id = replied.forward_from.id

        if target_id:
            try:
                await context.bot.send_message(target_id, f"💬 پاسخ ادمین: {update.message.text}")
                await update.message.reply_text("✅ پاسخ ارسال شد.")
            except Exception as e:
                await update.message.reply_text(f"❌ ارسال نشد: {e}")
        else:
            await update.message.reply_text(
                "⚠️ نتونستم بفهمم این پیام مربوط به کدوم کاربره.\n"
                "از دستور /reply <آیدی کاربر> <متن> استفاده کن."
            )
        return

    # پیام عادی از طرف کاربر -> فوروارد به ادمین + ثبت در نگاشت
    forwarded = await context.bot.forward_message(
        ADMIN_ID, update.effective_chat.id, update.message.message_id
    )
    context.bot_data.setdefault("user_map", {})[forwarded.message_id] = update.effective_user.id
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
app.add_handler(CommandHandler("reply", reply_command))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("ربات روشن شد...")
app.run_polling()
