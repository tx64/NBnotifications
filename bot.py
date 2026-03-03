import os
import json
import firebase_admin
from firebase_admin import credentials, messaging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# 1. Initialize Firebase
# We get the credentials from the Environment Variable "FIREBASE_CREDENTIALS"
firebase_config = os.environ.get("FIREBASE_CREDENTIALS")
if firebase_config:
    cred_dict = json.loads(firebase_config)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
else:
    print("Error: FIREBASE_CREDENTIALS not found!")

# 2. The /notify Command
async def send_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Security: Check if the sender is YOU
    MY_ID = os.environ.get("MY_TELEGRAM_ID")
    sender_id = str(update.effective_user.id)

    if sender_id != str(MY_ID):
        await update.message.reply_text("⛔ You are not authorized to send alerts.")
        return

    # Check if message text exists
    if not context.args:
        await update.message.reply_text("⚠️ Usage: /notify <Your Message>")
        return

    message_body = " ".join(context.args)

    # 3. Create the Notification for Firebase
    message = messaging.Message(
        notification=messaging.Notification(
            title='📢 College Update',
            body=message_body,
        ),
        topic='all', # Matches the topic in Android App
    )

    # 4. Send it!
    try:
        response = messaging.send(message)
        await update.message.reply_text(f"✅ Notification Sent! ID: {response}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# 5. Start the Bot
if __name__ == '__main__':
    TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

    if not TOKEN:
        print("Error: Bot Token not found!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("notify", send_alert))
        print("Bot is running...")
        app.run_polling()