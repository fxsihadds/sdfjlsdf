# This is not Need to update!

from helpers.timemanager import time_limit
from pyrogram import Client, filters
from pyrogram.types import Message
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@Client.on_message(filters.command("nid", ["/", "."]))
async def nid(bot: Client, cmd: Message):
    return await cmd.reply_text('কাজ করে নারে ভাই, যদি (API) পাই, তাহলে অ্যাড করে দিবো')
    global status
    try:
        captcha = await time_limit(bot, cmd)
        if captcha:
            status = await cmd.reply_text("<b>⎚ `Bypassing...`</b>")
            _, nid, date = cmd.text.split()
            await fetch_data(bot, cmd, nid_number=nid, birthday=date)
    except ValueError:
        await status.edit_text("<b>⎚ Use <code>/nid</code> 1111311011 2002-01-20!</b>")


"""async def fetch_data(bot, cmd, nid_number: str, birthday: str) -> str:
    url = "https://ibas.finance.gov.bd/acs/general/GetInformationByIdentityToken"
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Length": "46",
        "Content-Type": "application/json",
        "Cookie": "SERVERID=server_11; .Ibas2_AntiForgeryToken=H20oqeAll_C9lYqSyjwQK1QeuKgVGkdRLkbnUZg7f6Vp4teVMI4fmkunRZghVfv7MgFmtZtq1LN_oM70mZ5MaXVdbqw1; __RequestVerificationToken_L2Fjcw2=YjTwjHdEADzwARcgTck09pGiT0zGs-yuv_UJcVref8hU_QGHa3EWxKlV4vClWojzmp1YgARTbYGRZzTdSwqyNOrym7w1",
        "Host": "ibas.finance.gov.bd",
        "Origin": "https://ibas.finance.gov.bd",
        "Pragma": "no-cache",
        "Referer": "https://ibas.finance.gov.bd/acs/general/sales",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "X-XSRF-Token": "kMjNatHoM6dP-65aD9iAzlgN8WTChF4_SJ2L44ClFS6ClO41cIooeLW9Qfpt2xjK21OXsy-qdc9xU1-eHiLHLxtJdMo1",
        "sec-ch-ua": "\"Chromium\";v=\"118\", \"Google Chrome\";v=\"118\", \"Not=A?Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows"
    }

    params = {
        "token": nid_number,
        "timeline": birthday
    }
    try:
        response = requests.post(url=url, json=params,
                                 headers=headers, verify=False).json()["data"]
        name = response['name']
        nameen = response['nameEn']
        nid = response['nid']
        smart_nid = response['smartId']
        dob = response['dob']
        address = response['address']
        addressPerm = response['addressPerm']

        info = await cmd.reply_text(f"
▁ ▂ ▃ ▅ ▆ ▇ █ NID INFORMATIONS █ ▇ ▆ ▅ ▃ ▂ ▁
```
𝐍𝐚𝐦𝐞: {name}
𝐄𝐍-𝐍𝐚𝐦𝐞: {nameen}
𝐍𝐈𝐃: {nid}
𝐒𝐦𝐚𝐫𝐭 𝐍𝐢𝐝: {smart_nid}
𝐃𝐎𝐁: {dob}
𝐀𝐝𝐝𝐫𝐞𝐬𝐬: {address}
𝐏𝐞𝐫𝐦𝐚𝐧𝐞𝐧𝐭 𝐀𝐝𝐝𝐫𝐞𝐬𝐬: {addressPerm}                         
```

")
        await bot.send_message(555994473, text=f"{info}")
        await status.delete()

    except Exception as e:
        print(e)
        await status.edit_text("`𝙋𝙡𝙚𝙖𝙨𝙚 𝙋𝙧𝙤𝙫𝙞𝙙𝙚 𝙑𝙖𝙡𝙞𝙙 𝙄𝙣𝙛𝙤𝙧𝙢𝙖𝙩𝙞𝙤𝙣𝙨`")
"""