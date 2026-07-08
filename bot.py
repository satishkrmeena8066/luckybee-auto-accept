import sqlite3
from telegram import Update
from telegram.ext import (
    Application,
    ChatJoinRequestHandler,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
BOT_TOKEN = "8360228300:AAG43M1a7Hu2JqDz-i_Qffnum-V61h1AUfw"
CHANNEL_ID = -1004485039141
ADMIN_ID = 7324304740

db = sqlite3.connect("users.db", check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    first_name TEXT
)
""")

db.commit() 
broadcast_mode = {}
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    cursor.execute(
        "INSERT OR IGNORE INTO users(user_id,first_name) VALUES(?,?)",
        (user.id, user.first_name),
    )

    db.commit()

    await update.message.reply_text(
        f"👋 Welcome {user.first_name}\n\n"
        "🎉 Welcome to LuckyBee Team.\n\n"
        "You'll receive all offers here."
    )
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.chat_join_request.approve()

        user = update.chat_join_request.from_user

        cursor.execute(
            "INSERT OR IGNORE INTO users(user_id, first_name) VALUES(?, ?)",
            (user.id, user.first_name),
        )
        db.commit()

        try:
            await context.bot.send_message(
                chat_id=user.id,
                text=f"""🎉 Welcome {user.first_name}!

✅ Your request has been approved.

💚 Welcome to LuckyBee Team.

Stay connected for daily updates, offers and rewards."""
            )
        except Exception as e:
            print(f"DM Failed: {e}")

        print(f"Approved: {user.id}")

    except Exception as e:
        print(e)
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    broadcast_mode[update.effective_user.id] = True
    await update.message.reply_text(
        "📢 Broadcast message bhejo.\n\n"
        "Text, Photo, Video ya Document kuch bhi bhej sakte ho."
    )


async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        return

    if not broadcast_mode.get(user_id):
        return

    broadcast_mode[user_id] = False

    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()

    print(users)

    success = 0
    failed = 0

    for row in users:
        uid = row[0]
print(f"Sending to {uid}")
        try:
            if update.message.photo:
                await context.bot.send_photo(
                    uid,
                    update.message.photo[-1].file_id,
                    caption=update.message.caption or ""
                )

            elif update.message.video:
                await context.bot.send_video(
                    uid,
                    update.message.video.file_id,
                    caption=update.message.caption or ""
                )

            elif update.message.document:
                await context.bot.send_document(
                    uid,
                    update.message.document.file_id,
                    caption=update.message.caption or ""
                )

            else:
                await context.bot.send_message(
                    uid,
                    update.message.text
                )

            success += 1

        except Exception as e:
    print(f"❌ Failed {uid}: {repr(e)}")
    failed += 1
    await update.message.reply_text(
        f"""✅ Broadcast Complete

👥 Total Users: {len(users)}
✅ Success: {success}
❌ Failed: {failed}
"""
    )
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(ChatJoinRequestHandler(approve))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(MessageHandler(filters.ALL, broadcast_handler))
print("LuckyBee Bot Started...")
app.run_polling(
    allowed_updates=Update.ALL_TYPES
)
