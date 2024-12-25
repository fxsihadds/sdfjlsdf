import re
import os
from pyrogram import filters, Client
from pyrogram.types import Message


EMAIL_PASSWORD_REGEX = r"(\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b:\S+)"


def extract_email_passwords(text):
    email_passwords = re.findall(EMAIL_PASSWORD_REGEX, text)
    return email_passwords


@Client.on_message(filters.command('gscr'))
async def scraper_command(client, message):
    status = await message.reply("<b>⎚ `Extracting...`</b>")
    text_to_scrape = None

    if message.reply_to_message:
        if message.reply_to_message.document:
            # Scraping from a replied document
            document = message.reply_to_message.document

            if document.file_name.endswith('.txt'):
                # Check if the file is a text file
                file_path = await client.download_media(document)

                with open(file_path, 'r', encoding='utf-8') as file:
                    text_to_scrape = file.read()

                # Remove the temporary file
                os.remove(file_path)
            else:
                await status.edit_text(text='<b>Please provide a text file (.txt) to scrape email:password combinations😞.</b>')
                return
        elif message.reply_to_message.text:
            # Scraping from a replied text message
            text_to_scrape = message.reply_to_message.text

    if text_to_scrape is None:
        # If no text to scrape is found in the replied message, try the command message
        command_text = message.text.split(' ', 1)
        if len(command_text) > 1:
            text_to_scrape = command_text[1]

    if text_to_scrape is None:
        await status.edit_text(text='<b>No text found to scrape email:password combinations😞.</b>')
        return

    email_passwords = extract_email_passwords(text_to_scrape)

    if len(email_passwords) > 0:
        # Create a file with the extracted email:password combinations
        filename = os.path.basename(file_path)
        with open(filename, 'w', encoding='utf-8') as file:
            for email_password in email_passwords:
                file.write(email_password + '\n')

        # Reply with the file
        await client.send_document(
            chat_id=message.chat.id,
            document=filename,
            caption=f'<b>Extracted {len(email_passwords)} email:password</b>'
        )

        # Remove the file after sending
        os.remove(filename)
        await status.delete()
    else:
        await status.edit_text(text='<b>No email:password combinations found in the provided text ❌.</b>')