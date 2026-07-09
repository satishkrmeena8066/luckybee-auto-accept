import os
import psycopg
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

DATABASE_URL = os.environ["DATABASE_URL"]

db = psycopg.connect(DATABASE_URL)
db.autocommit = True
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS channels (
    chat_id BIGINT PRIMARY KEY,
    title TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS support_messages (
    admin_msg_id BIGINT PRIMARY KEY,
    user_id BIGINT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS welcome_settings (
    id INT PRIMARY KEY DEFAULT 1,
    message_type TEXT,
    file_id TEXT,
    caption TEXT,
    button_text TEXT,
    button_url TEXT
)
""")
broadcast_mode = {}
support_mode = {}
welcome_mode = {}
async def save_channel(chat):
    cursor.execute(
        """
        INSERT INTO channels (chat_id, title)
        VALUES (%s, %s)
        ON CONFLICT (chat_id) DO NOTHING
        """,
        (chat.id, chat.title),
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    cursor.execute(
        """
        INSERT INTO users (user_id, first_name)
        VALUES (%s, %s)
        ON CONFLICT (user_id) DO NOTHING
        """,
        (user.id, user.first_name),
    )

    await update.message.reply_text(
        f"👋 Welcome {user.first_name}!\n\n🎉 Welcome to LuckyBee Team.\n\nYou'll receive all offers here."
    )
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.chat_join_request.approve()

        user = update.chat_join_request.from_user

        cursor.execute(
            """
            INSERT INTO users (user_id, first_name)
            VALUES (%s, %s)
            ON CONFLICT (user_id) DO NOTHING
            """,
            (user.id, user.first_name),
        )

        chat = update.chat_join_request.chat
        await save_channel(chat)       
       
        try:
        cursor.execute(
            "SELECT message_type, file_id, caption FROM welcome_settings WHERE id=1"
        )

        row = cursor.fetchone()

        if row:
            message_type, file_id, caption = row

            if message_type == "photo":
                await context.bot.send_photo(
                    chat_id=user.id,
                    photo=file_id,
                    caption=caption
                )

            elif message_type == "video":
                await context.bot.send_video(
                    chat_id=user.id,
                    video=file_id,
                    caption=caption
                )

            else:
                await context.bot.send_message(
                    chat_id=user.id,
                    text=caption
                )

        else:
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
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM channels")
    total_channels = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM support_messages")
    total_support = cursor.fetchone()[0]

    await update.message.reply_text(
        f"""📊 LuckyBee Bot Stats

👥 Total Users : {total_users}
📢 Total Channels : {total_channels}
💬 Support Messages : {total_support}
"""
    )
async def channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    cursor.execute(
        "SELECT chat_id, title FROM channels ORDER BY title"
    )

    rows = cursor.fetchall()

    if not rows:
        await update.message.reply_text("❌ No channels found.")
        return

    text = "📢 LuckyBee Channels\n\n"

    for i, row in enumerate(rows, start=1):
        text += f"{i}. {row[1]}\n"
        text += f"🆔 {row[0]}\n\n"

    await update.message.reply_text(text)
async def users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    cursor.execute(
        "SELECT user_id, first_name FROM users ORDER BY user_id DESC LIMIT 50"
    )

    rows = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]

    if not rows:
        await update.message.reply_text("❌ No users found.")
        return

    text = f"👥 Total Users: {total}\n\n"

    for i, row in enumerate(rows, start=1):
        text += f"{i}. {row[1]}\n"
        text += f"🆔 {row[0]}\n\n"

    await update.message.reply_text(text)  
async def setwelcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    welcome_mode[update.effective_user.id] = True

    await update.message.reply_text(
        "📤 Welcome message bhejo.\n\n"
        "Text, Photo ya Video bhej sakte ho."
    )  
async def welcome_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not welcome_mode.get(update.effective_user.id):
        return

    welcome_mode[update.effective_user.id] = False

    msg = update.message

    message_type = "text"
    file_id = None
    caption = ""
    button_text = ""
    button_url = ""

    if msg.text:
        caption = msg.text

    elif msg.photo:
        message_type = "photo"
        file_id = msg.photo[-1].file_id
        caption = msg.caption or ""

    elif msg.video:
        message_type = "video"
        file_id = msg.video.file_id
        caption = msg.caption or ""

    else:
        await update.message.reply_text(
            "❌ Sirf Text, Photo ya Video allowed hai."
        )
        return

    cursor.execute(
        """
        DELETE FROM welcome_settings
        """
    )

    cursor.execute(
        """
        INSERT INTO welcome_settings
        (id, message_type, file_id, caption, button_text, button_url)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            1,
            message_type,
            file_id,
            caption,
            button_text,
            button_url,
        ),
    )

    await update.message.reply_text(
        "✅ Welcome Message Saved Successfully!"
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
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        return

    if not update.message:
        return

    admin_msg = await context.bot.forward_message(
        chat_id=ADMIN_ID,
        from_chat_id=update.effective_chat.id,
        message_id=update.message.message_id,
    )

    cursor.execute(
        """
        INSERT INTO support_messages (admin_msg_id, user_id)
        VALUES (%s, %s)
        ON CONFLICT (admin_msg_id) DO NOTHING
        """,
        (admin_msg.message_id, update.effective_user.id),
    )
async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not update.message.reply_to_message:
        return

    cursor.execute(
        "SELECT user_id FROM support_messages WHERE admin_msg_id=%s",
        (update.message.reply_to_message.message_id,),
    )

    row = cursor.fetchone()

    if not row:
        return

    uid = row[0]
    msg = update.message

    if msg.text:
        await context.bot.send_message(
            chat_id=uid,
            text=msg.text
        )

    elif msg.photo:
        await context.bot.send_photo(
            chat_id=uid,
            photo=msg.photo[-1].file_id,
            caption=msg.caption or ""
        )

    elif msg.video:
        await context.bot.send_video(
            chat_id=uid,
            video=msg.video.file_id,
            caption=msg.caption or ""
        )

    elif msg.document:
        await context.bot.send_document(
            chat_id=uid,
            document=msg.document.file_id,
            caption=msg.caption or ""
        )

    elif msg.voice:
        await context.bot.send_voice(
            chat_id=uid,
            voice=msg.voice.file_id
        )

    elif msg.audio:
        await context.bot.send_audio(
            chat_id=uid,
            audio=msg.audio.file_id,
            caption=msg.caption or ""
        )

    elif msg.sticker:
        await context.bot.send_sticker(
            chat_id=uid,
            sticker=msg.sticker.file_id
        )
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(ChatJoinRequestHandler(approve))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("channels", channels))
app.add_handler(CommandHandler("users", users))
app.add_handler(CommandHandler("setwelcome", setwelcome))
app.add_handler(
    MessageHandler(filters.ALL, broadcast_handler),
    group=0
)
app.add_handler(
    MessageHandler(
        filters.TEXT | filters.PHOTO | filters.VIDEO,
        welcome_handler,
    ),
    group=1,
)
app.add_handler(
    MessageHandler(
        (
            filters.TEXT
            | filters.PHOTO
            | filters.VIDEO
            | filters.Document.ALL
            | filters.VOICE
            | filters.AUDIO
            | filters.Sticker.ALL
        ) & ~filters.COMMAND,
        support,
    ),
    group=1,
)

app.add_handler(
    MessageHandler(filters.REPLY, admin_reply),
    group=2
)
print("LuckyBee Bot Started...")
app.run_polling(
    allowed_updates=Update.ALL_TYPES
)
