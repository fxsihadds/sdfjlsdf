# This is Under Development

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery


@Client.on_message(filters.command('gdot'))
async def gmail_dot(bot: Client, cmd: Message):
    await cmd.reply_text(
        text='Gmail Dot Trick!',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        'Generate', callback_data='NewGenerate'),
                    InlineKeyboardButton('Help', callback_data='Reload_gmail'),
                    InlineKeyboardButton('About', callback_data='about_gmail')
                ],
                [
                    InlineKeyboardButton(
                        'Read Our Doc', url='https://t.me/your_channel')
                ]
            ]
        )
    )
