import sqlite3
from telegram import Update
from telegram.ext import (
    Application,
    ChatJoinRequestHandler,
    CommandHandler,
    ContextTypes,
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
        app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(ChatJoinRequestHandler(approve))

print("LuckyBee Bot Started...")

app.run_polling(
    allowed_updates=["message", "chat_join_request"]
)
