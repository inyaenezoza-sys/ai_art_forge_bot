import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Configuration ---
# Pollinations.ai free image generation endpoint
POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{}"
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set!")

# --- Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the /start command is issued."""
    user = update.effective_user
    await update.message.reply_text(
        f"Hi {user.first_name}! 🎨 I'm your AI Art Forge Bot.\n\n"
        "Just send me a text description of the image you want, and I'll generate it for you.\n"
        "For example: 'a futuristic cityscape at sunset, cyberpunk style'"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate an image from the user's text prompt."""
    prompt = update.message.text
    await update.message.reply_text(f"🎨 Generating image for: '{prompt}'... This may take a few seconds.")

    # Construct the URL for Pollinations.ai (it returns an image directly)
    # The prompt is URL-encoded to handle spaces and special characters
    import urllib.parse
    encoded_prompt = urllib.parse.quote(prompt)
    image_url = POLLINATIONS_URL.format(encoded_prompt)

    try:
        # Download the image from Pollinations.ai
        response = requests.get(image_url, stream=True)
        response.raise_for_status()

        # Send the image back to the user
        await update.message.reply_photo(photo=response.raw)
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"❌ Sorry, I couldn't generate that image. Error: {e}")

# --- Main Function ---
def main():
    # Create the Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))

    # Register a handler for all text messages (non-command)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot (using polling - simpler for Railway)
    print("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
