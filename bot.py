from telegram import Update
from telegram.ext import Application, ChatJoinRequestHandler, ContextTypes

BOT_TOKEN = "8360228300:AAG43M1a7Hu2JqDz-i_Qffnum-V61h1AUfw"
CHANNEL_ID = -1004485039141

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Approve Join Request
        await update.chat_join_request.approve()

        user = update.chat_join_request.from_user
        user_id = user.id
        first_name = user.first_name

        print(f"Approved: {user_id}")

        # Send Welcome Message
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"""🎉 Welcome {first_name}!

✅ Your join request has been approved successfully.

💚 Thank you for joining LuckyBee Team.

Stay connected for daily updates and exciting offers!"""
            )
            print(f"Welcome message sent to {user_id}")

        except Exception as e:
            print(f"DM Failed: {e}")

    except Exception as e:
        print(f"Approve Failed: {e}")

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(ChatJoinRequestHandler(approve))

print("LuckyBee Bot Started...")

app.run_polling(
    allowed_updates=["chat_join_request"]
)
