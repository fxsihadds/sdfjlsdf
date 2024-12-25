from pyrogram import Client, filters, enums
from pyrogram.types import Message
import requests as r


async def url_requests(bot, cmd, url, extension=None):
    endpoint = 'https://tinyurl.com/api-create.php?'
    payload = {"url": url}
    try:
        res = r.get(url=endpoint, params=payload)
    except Exception as e:
        await cmd.reply_text('''╰┈➤ꜱᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ, ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ☠️''')
        print(e)
    else:
        message = f"""
<b>🟢ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʏ ᴄʀᴇᴀᴛᴇᴅ🟢</b>
﹌﹌﹌﹌﹌﹌﹌﹌﹌﹌﹌﹌
🔗ᴍᴀɪɴ ᴜʀʟ: {url}
🔗ꜱʜᴏʀᴛ ᴜʀʟ: {res.text}

"""
        await cmd.reply_text(message)


@Client.on_message(filters.command('surl'))
async def shorturl(bot: Client, cmd: Message):
    await bot.send_chat_action(chat_id=cmd.chat.id, action=enums.ChatAction.TYPING)
    try:
        _, m_url = cmd.text.split()
    except ValueError as e:
        await cmd.reply_text('<b>╰┈➤​Send​ Any Link For Short Url</b>​')
    else:
        await url_requests(bot, cmd, m_url)
