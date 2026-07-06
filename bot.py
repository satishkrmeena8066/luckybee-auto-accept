from telegram import Update
from telegram.ext import Application, ChatJoinRequestHandler, ContextTypes

BOT_TOKEN = "8360228300:AAGWZjGV4v6JTeYcz72zFuxGOCst6VBVlpQ"
CHANNEL_ID = -1004485039141

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.approve_chat_join_request(
            chat_id=CHANNEL_ID,
            user_id=update.chat_join_request.from_user.id
        )
        print(f"Approved: {update.chat_join_request.from_user.id}")
    except Exception as e:
        print(e)

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(ChatJoinRequestHandler(approve))
app.run_polling()
