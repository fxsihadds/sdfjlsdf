import asyncio
from pyrogram import Client
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from configparser import ConfigParser
from random import randint

config = ConfigParser()
config.read('config.ini')
chennel_id = config['pyrogram']['update_chennel']


async def ForceSub(bot: Client, cmd: Message):
    try:
        invite_link = await bot.create_chat_invite_link(int(chennel_id))
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return 400
    try:
        user = await bot.get_chat_member(int(chennel_id), user_id=cmd.from_user.id)
        if user.status == "banned":
            await bot.send_message(
                chat_id=cmd.from_user.id,
                text="Access Denied ⚠",
            )
            return 400
    except UserNotParticipant:
        await bot.send_message(
            chat_id=cmd.from_user.id,
            text="Pʟᴇᴀsᴇ Jᴏɪɴ Mʏ Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🤖 Jᴏɪɴ ᴍʏ ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ 🤖", url=invite_link.invite_link)
                    ]
                ]
            ),
        )
        return 400
    except Exception:
        await bot.send_message(
            chat_id=cmd.from_user.id,
            text="Something Went Wrong.)",
        )
        return 400


class Verify_user:
    def __init__(self):
        pass


    def check_user(self, user_id):
        pass



    def robot(self, inp):
        f1 = randint(5, 9)
        f2 = randint(1, 4)
        
