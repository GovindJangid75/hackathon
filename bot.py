from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes
from telegram.ext import filters
import pandas as pd

# Define the start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the Crop Price Bot! Use /get_price to check crop prices or /upload_csv to upload price data."
    )

# Define the get_price command
async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    crop = " ".join(context.args)
    # Mock data for now
    prices = {
        "rice": "₹40 per kg",
        "wheat": "₹30 per kg",
        "mustard": "₹45 per kg"
    }
    price = prices.get(crop.lower(), "Sorry, I don't have the price for that crop.")
    await update.message.reply_text(f"The price of {crop} is: {price}")

# Define the upload_csv command
async def upload_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please upload a CSV file containing crop prices.")

# Handle the CSV file upload
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    if document.mime_type == 'text/csv':
        file = await document.get_file()
        await file.download_to_drive("crop.csv")  # Save file locally
        await update.message.reply_text("CSV file uploaded successfully! Now you can check crop prices.")

        # Load the CSV data into pandas
        try:
            data = pd.read_csv("crop.csv")
            print(data)  # For now, just print it to the terminal
        except Exception as e:
            await update.message.reply_text(f"Error parsing CSV file: {e}")
    else:
        await update.message.reply_text("Please upload a valid CSV file.")

# Main function to set up the bot
def main():
    token = 'YOUR_BOT_TOKEN_HERE'  # Replace with your bot's token from BotFather
    application = ApplicationBuilder().token(token).build()

    # Add command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('get_price', get_price))
    application.add_handler(CommandHandler('upload_csv', upload_csv))
    application.add_handler(MessageHandler(filters.Document.MIME_TYPE("text/csv"), handle_document))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
