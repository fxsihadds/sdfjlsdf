from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    InputMediaPhoto,
)
import requests


@Client.on_message(filters.command("fake", ["/", "."]))
async def rand_helper_command(_, cmd: Message):
    status = await cmd.reply_text("<b>⎚ `Generating...`</b>")
    try:
        us = cmd.text.split()[1]
        api = requests.get(f"https://randomuser.me/api/?nat={us}").json()
    except IndexError as err:
        await status.edit_text("`Please Use Country Code!`")
    else:

        mr = api["results"][0]["name"]["title"]
        nombre = api["results"][0]["name"]["first"]
        last = api["results"][0]["name"]["last"]
        loca = api["results"][0]["location"]["street"]["name"]
        nm = api["results"][0]["location"]["street"]["number"]
        city = api["results"][0]["location"]["city"]
        state = api["results"][0]["location"]["state"]
        country = api["results"][0]["location"]["country"]
        postcode = api["results"][0]["location"]["postcode"]
        latitude = api["results"][0]["location"]["coordinates"]["latitude"]
        longitude = api["results"][0]["location"]["coordinates"]["longitude"]
        photo = api["results"][0]["picture"]["large"]

        text = f"""
⎚ 𝐅𝐚𝐤𝐞 𝐀𝐝𝐝𝐫𝐞𝐬𝐬
⎚ 𝐍𝐚𝐦𝐞: <code>{mr} {nombre} {last}</code>
⎚ 𝐒𝐭𝐫𝐞𝐞𝐭:  <code>{state}</code>
⎚ 𝐂𝐢𝐭𝐲: <code>{city}</code>
⎚ 𝐒𝐭𝐚𝐭𝐞:<code> {loca} {nm}</code>
⎚ 𝐏𝐨𝐬𝐭𝐜𝐨𝐝𝐞: <code> {postcode}</code>
⎚ 𝐂𝐨𝐮𝐧𝐭𝐫𝐲: <code>{country}</code>
⎚ 𝐂𝐡𝐞𝐜𝐤𝐞𝐝 𝐁𝐲 <code> @{cmd.from_user.username}</code>
    """
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("ReGenerate", callback_data="regenerateadds")],
            ]
        )
        await status.edit_text(text, reply_markup=keyboard)


async def regenerate_callback(_, callback_query):
    api = requests.get("https://randomuser.me/api/").json()

    mr = api["results"][0]["name"]["title"]
    nombre = api["results"][0]["name"]["first"]
    last = api["results"][0]["name"]["last"]
    loca = api["results"][0]["location"]["street"]["name"]
    nm = api["results"][0]["location"]["street"]["number"]
    city = api["results"][0]["location"]["city"]
    state = api["results"][0]["location"]["state"]
    country = api["results"][0]["location"]["country"]
    postcode = api["results"][0]["location"]["postcode"]
    latitude = api["results"][0]["location"]["coordinates"]["latitude"]
    longitude = api["results"][0]["location"]["coordinates"]["longitude"]
    photo = api["results"][0]["picture"]["large"]

    text = f"""
<b> 
⎚ 𝐅𝐚𝐤𝐞 𝐀𝐝𝐝𝐫𝐞𝐬𝐬
⎚ 𝐍𝐚𝐦𝐞: <code>{mr} {nombre} {last}</code>
⎚ 𝐒𝐭𝐫𝐞𝐞𝐭:  <code>{state}</code>
⎚ 𝐂𝐢𝐭𝐲: <code>{city}</code>
⎚ 𝐒𝐭𝐚𝐭𝐞:<code> {loca} {nm}</code>
⎚ 𝐏𝐨𝐬𝐭𝐜𝐨𝐝𝐞: <code> {postcode}</code>
⎚ 𝐂𝐨𝐮𝐧𝐭𝐫𝐲: <code>{country}</code>
⎚ 𝐂𝐡𝐞𝐜𝐤𝐞𝐝 𝐁𝐲 <code> @{callback_query.from_user.username}</code>
"""
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Regenerate", callback_data="regenerateadds")],
        ]
    )
    # await callback_query.edit_message_media(media=InputMediaPhoto(media=photo),reply_markup=keyboard)
    await callback_query.edit_message_caption(caption=text, reply_markup=keyboard)
