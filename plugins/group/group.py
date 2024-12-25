from pyrogram.types import Message
from pyrogram import Client, filters
import os 
from .group_helper.admin import admin_filter

# This Func For Groupe and Channel Pin Msg
@Client.on_message(filters.command('pin') & filters.create(admin_filter))
async def _pin(_, cmd:Message):
    if not cmd.reply_to_message:return
    await cmd.reply_to_message.pin() 


# This Func For Groupe and Channel unPin Msg
@Client.on_message(filters.command('unpin') & filters.create(admin_filter))
async def _unpin(Client, cmd:Message):
    if not cmd.reply_to_message: return
    await cmd.reply_to_message.unpin()



    