from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from emoji import emojize

buttons_l = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(emojize(':gear: Generate'), callback_data='generatetemp'),
            InlineKeyboardButton(emojize(':counterclockwise_arrows_button: Refresh'), callback_data='refreshtemp'),
            InlineKeyboardButton(emojize(':cross_mark: Close'), callback_data='closetemp')
        ]
    ])

msg_buttons = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(emojize(':eyes: View message'), callback_data='view_msgtemp'),
            InlineKeyboardButton(emojize(':cross_mark: Close'), callback_data='closetemp')
        ]
    ])



@Client.on_message(filters.command('temp'))
async def start_msg(client, message):
    await message.reply("**Generate a Email Now!**",
                        reply_markup=buttons_l)
    
