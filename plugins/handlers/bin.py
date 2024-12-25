import requests
from pyrogram import Client, filters
from helpers.timemanager import ratelimiters



@Client.on_message(filters.command("bin"))
@ratelimiters
async def cmds(_, cmd):
    try:
        BIN = cmd.text.split("/bin", 1)[1].strip()
    except IndexError:
        return await cmd.reply("<b>⎚ Use <code>/bin 456789</code></b>")

    if not BIN:
        return await cmd.reply("<b>⎚ Use <code>/bin 456789</code></b>")

    bincode = 6
    BIN = BIN[:bincode]
    req = requests.get(f"https://bins.antipublic.cc/bins/{BIN}").json()

    if 'bin' not in req:
        await cmd.reply_text(f'<b>⎚ 𝗕𝗶𝗻 ⇾ not found <code>{BIN} ❌</code></b>')

    else:
        brand = req['brand']
        country = req['country']
        country_name = req['country_name']
        country_flag = req['country_flag']
        country_currencies = req['country_currencies']
        bank = req['bank']
        level = req['level']
        typea = req['type']

        message_text = f"""
<b>⎚ BIN Information</b>
<b>BIN</b>: <code>{BIN}</code>
<b>Country</b>: {country} | {country_flag} | {country_name}
<b>Status</b>: Approved ✅
<b>Data</b>: {brand} - {typea} - {level}
<b>Bank</b>: {bank}
<b>Response Time</b>: <code>1.6 seconds</code>
⎚ 𝐂𝐡𝐞𝐜𝐤𝐞𝐝 𝐁𝐲: <b>@{cmd.from_user.username}</b>
"""
        await cmd.reply_text(message_text)

