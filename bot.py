import os
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Replace with your KrakenFiles API URL and Bot Token
KRAKEN_API_URL = 'https://krakenfiles.com/api/v2/file/upload'
TELEGRAM_BOT_TOKEN = '5707293090:AAHGLlHSx101F8T1DQYdcb9_MkRAjyCbt70'

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! Send me a file and I will upload it to KrakenFiles.')

def upload_to_krakenfiles(file_path):
    # Prepare file upload
    with open(file_path, 'rb') as f:
        files = {'file': f}
        try:
            response = requests.post(KRAKEN_API_URL, files=files)
            response_data = response.json()

            if response.status_code == 200 and response_data.get('success'):
                # Return the file link
                return response_data['data']['file']['url']
            else:
                return None
        except Exception as e:
            print(f"Error uploading to KrakenFiles: {e}")
            return None

def handle_file(update: Update, context: CallbackContext) -> None:
    file = update.message.document or update.message.photo[-1] if update.message.photo else None

    if file:
        # Download the file from Telegram
        file_id = file.file_id
        new_file = context.bot.get_file(file_id)
        file_path = new_file.download()

        # Upload to KrakenFiles
        kraken_link = upload_to_krakenfiles(file_path)

        # Clean up the local file after upload
        os.remove(file_path)

        if kraken_link:
            update.message.reply_text(f'File uploaded successfully! Here is your link: {kraken_link}')
        else:
            update.message.reply_text('Failed to upload file to KrakenFiles.')
    else:
        update.message.reply_text('Please send a valid file.')

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)

    # Add handlers
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(MessageHandler(Filters.document | Filters.photo, handle_file))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
