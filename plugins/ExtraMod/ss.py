# This is under developement

"""from pyrogram import Client, filters
from pyrogram.types import Message
import os
from pyppeteer import launch


@Client.on_message(filters.command(["ss", ".", "/"]) & filters.private)
async def take_screenshot(bot: Client, cmd: Message):
    try:
        status = await cmd.reply_text("<b>⎚ `Screenshot Taking...`</b>")
        _, web = cmd.text.split(" ", 1)
    except ValueError as e:
        await status.edit_text('</b>Please Using Like /ss Then Any Url.</b>')
    await take_screenshot_and_reply(bot, cmd, cmd.chat.id, web)
    await status.delete()


async def take_screenshot_and_reply(bot: Client, cmd: Message, chat_id: int, url: str):
    browser = await launch()
    page = await browser.newPage()
    await page.goto(url)
    screenshot_path = "screenshot.png"
    await page.screenshot({"path": screenshot_path})
    await browser.close()
    await bot.send_photo(chat_id, photo=screenshot_path, caption=url)
    os.remove(screenshot_path)
"""