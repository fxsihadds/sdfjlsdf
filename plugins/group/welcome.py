from pyrogram import filters, Client
from pyrogram.types import Message
from .group_helper.admin import admin_filter

# force to Admin any Groupe:


# Event handler for chat member updates
@Client.on_chat_member_updated()
async def handle_chat_member_updated(bot: Client, cmd: Message):
    await bot.send_message(cmd.chat.id, "Welcome!")


# For Count
@Client.on_message(filters.command('count') & (filters.group & filters.create(admin_filter)))
async def count_membar(bot: Client, cmd: Message):
    if cmd.reply_to_message:
        return
    _count = await bot.get_chat_members_count(chat_id=cmd.chat.id)
    await cmd.reply_text(f"<b>`Total Members In The Group:` {_count}</b>")
