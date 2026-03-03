import os
import json
import firebase_admin
from firebase_admin import credentials, messaging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from flask import Flask
from threading import Thread

# --- 1. THE FAKE WEBSITE (To trick Render) ---
app_web = Flask('')

@app_web.route('/')
def home():
    return "I am alive! Bot is running."

def run_http():
    # Render assigns a PORT via environment variable, we must listen on it
    port_number = int(os.environ.get('PORT', 8080))
    app_web.run(host='0.0.0.0', port=port_number)

def keep_alive():
    t = Thread(target=run_http)
    t.start()

# --- 2. FIREBASE SETUP ---
firebase_config = os.environ.get("FIREBASE_CREDENTIALS")
if firebase_config:
    # Handle potential JSON parsing errors
    try:
        cred_dict = json.loads(firebase_config)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Firebase Error: {e}")
else:
    print("Warning: FIREBASE_CREDENTIALS not found.")

# --- 3. BOT LOGIC ---
async def send_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    MY_ID = os.environ.get("MY_TELEGRAM_ID")
    sender_id = str(update.effective_user.id)
    
    if sender_id != str(MY_ID):
        await update.message.reply_text("⛔ You are not authorized.")
        return

    if not context.args:
        await update.message.reply_text("⚠️ Usage: /notify <Your Message>")
        return

    message_body = " ".join(context.args)

    message = messaging.Message(
        notification=messaging.Notification(
            title='📢 College Update',
            body=message_body,
        ),
        topic='all',
    )

    try:
        response = messaging.send(message)
        await update.message.reply_text(f"✅ Notification Sent!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# --- 4. START EVERYTHING ---
if __name__ == '__main__':
    # Start the fake website first
    keep_alive()
    
    # Start the bot
    TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        print("Error: Bot Token not found!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("notify", send_alert))
        print("Bot is running...")
        app.run_polling()
