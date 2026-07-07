from telegram import Update
from telegram.ext import Application, ChatJoinRequestHandler, ContextTypes

BOT_TOKEN = "8360228300:AAG43M1a7Hu2JqDz-i_Qffnum-V61h1AUfw"
CHANNEL_ID = -1004485039141

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.chat_join_request.approve()
        print(f"Approved: {update.chat_join_request.from_user.id}")
    except Exception as e:
        print(e)

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(ChatJoinRequestHandler(approve))

print("Bot Started...")
app.run_polling(allowed_updates=["chat_join_request"])
