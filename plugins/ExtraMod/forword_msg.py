import re
import os
from urllib.parse import urlparse
from pyrogram import Client, filters
from pyrogram.types import Message
from userc import LOGGER, user
from config import Config 


def remove_duplicates(messages):
    unique_messages = list(set(messages))
    duplicates_removed = len(messages) - len(unique_messages)
    return unique_messages, duplicates_removed

async def scrape_messages(_, channel_username, limit, start_number=None):
    messages = []
    count = 0
    pattern = r"(?i)(https\:\/\/){1}((t\.me|telegram\.me)\/){1}(joinchat\/)?(([\+\_\-a-zA-Z0-9])+)$"
    async for message in user.search_messages(channel_username):
        if count >= limit:
            break
        text = message.text if message.text else message.caption
        print(text)
        if text:
            matched_messages = re.findall(pattern, text)
            if matched_messages:
                formatted_messages = []
                for matched_message in matched_messages:
                    print()
                    # Join tuple elements into a single string
                    matched_message_str = ''.join(matched_message)
                    extracted_values = re.findall(r'\d+', matched_message_str)
                    if len(extracted_values) == 4:
                        formatted_messages.append(f"{extracted_values}")
                messages.extend(formatted_messages)
                count += len(formatted_messages)
    if start_number:
        messages = [msg for msg in messages if msg.startswith(start_number)]
    messages = messages[:limit]
    return messages


@Client.on_message(filters.command('linkscr'))
async def scr_cmd(bot: Client, cmd: Message):
    args = cmd.text.split()[1:]
    if len(args) < 2 or len(args) > 3:
        await cmd.reply_text("<b>/ccscr channel username and amount</b>")
        return

    channel_identifier = args[0]
    limit = int(args[1])
    max_lim = 50000
    if limit > max_lim:
        await cmd.reply_text(f"<b>Amount over Max limit is {max_lim} </b>")
        return

    start_number = args[2] if len(args) == 3 else None
    parsed_url = urlparse(channel_identifier)
    channel_username = parsed_url.path.lstrip('/') if not parsed_url.scheme else channel_identifier
    print(f"Channel username: {channel_username}")
    try:
        chat = await user.get_chat(channel_username)
        channel_name = chat.title
    except Exception as err:
        await cmd.reply_text("<b> Incorrect username</b>")
        LOGGER.error("FROM msg SCRAPE: %s", err)
        return

    temporary_msg = await cmd.reply_text("<b>`Scraping.....`</b>")
    scrapped_results = await scrape_messages(user, chat.id, limit, start_number)
    print(f"Scrapped results: {scrapped_results}")

    unique_messages, duplicates_removed = remove_duplicates(scrapped_results)
    if unique_messages:
        file_name = f"x{len(unique_messages)}_{channel_name.replace(' ', '_')}.txt"
        with open(file_name, 'w') as f:
            f.write("\n".join(unique_messages))
        with open(file_name, 'rb') as f:
            caption = (
                f"<b>Link Scrapped ✅</b>\n"
                f"<b>━━━━━━━━━━━━━━━━</b>\n"
                f"<b>Source:</b> <code>{channel_name}</code>\n"
                f"<b>Amount:</b> <code>{len(unique_messages)}</code>\n"
                f"<b>Duplicates Removed:</b> <code>{duplicates_removed}</code>\n"
                f"<b>━━━━━━━━━━━━━━━━</b>\n"
                f"<b>Scrapper By: {cmd.from_user.first_name}</b>\n"
            )
            await temporary_msg.delete()
            await bot.send_document(cmd.chat.id, f, caption=caption)
        os.remove(file_name)
    else:
        await temporary_msg.delete()
        await cmd.reply_text("<b>No Link Found</b>")
