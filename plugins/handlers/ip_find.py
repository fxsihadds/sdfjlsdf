import requests
from pyrogram import Client, filters
from pyrogram.types import Message


@Client.on_message(filters.command("ip"))
async def ip_helper_command(_, message):
    zipcode = message.text[len('/ip '):]
    if not zipcode:
        await message.reply("<b>⎚ Use <code>/ip 1.1.1.1</code><b>")
        return
    spli = zipcode.split()
    ips = spli[0]
    if not spli:
        await message.reply_text(f'<b>⎚ Use <code>/ip 1.1.1.1</code><b>')
        return

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'es-ES,es;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36', }

    response = requests.get(
        f'http://ipwho.is/{ips}', headers=headers, verify=False).json()
    ip = response['ip']
    flag = response['flag']['emoji']
    connection = response['connection']['asn']
    connection1 = response['connection']['org']
    connection2 = response['connection']['isp']
    connection3 = response['connection']['domain']
    timezone = response['timezone']['id']
    timezone1 = response['timezone']['abbr']
    timezone2 = response['timezone']['is_dst']
    timezone3 = response['timezone']['utc']
    timezone4 = response['timezone']['current_time']

    await message.reply(f"""<b>
⎚ 𝐈𝐏 𝐂𝐇𝐄𝐂𝐊 
⎚ 𝐈𝐏:  <code>{ip}</code> ✅
━━━━━━━━━━━━━━
⎚ 𝐂𝐢𝐭𝐲: <code>{timezone} {flag}</code>
⎚ 𝐈𝐏𝐬: <code>{connection2}</code>
⎚ 𝐀𝐛𝐛𝐫𝐞𝐯𝐢𝐚𝐭𝐢𝐨𝐧 : <code>{timezone1}</code>
⎚ 𝐃𝐨𝐦𝐚𝐢𝐧: <code>{connection3}</code>
⎚ 𝐎𝐫𝐠𝐚𝐧𝐢𝐳𝐚𝐭𝐢𝐨𝐧: <code>{connection1}</code>
⎚ Checked By: @{message.from_user.username}
""")
