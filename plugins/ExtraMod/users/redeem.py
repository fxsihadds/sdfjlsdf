import aiofiles
from pyrogram import Client, filters


async def remove_redeem_code(redeem_code, user_redeem):
    updated_redeem_code = [code.strip()
                           for code in redeem_code if code.strip() != user_redeem]
    async with aiofiles.open("plugins/ExtraMod/users/redeem.txt", mode="w+", encoding="utf-8") as redeem_file:
        await redeem_file.write("\n".join(updated_redeem_code))



@Client.on_message(filters.command("redeem"))
async def redeem_cmd(app_client, message):
    async with aiofiles.open("plugins/ExtraMod/users/redeem.txt", mode="r+", encoding="utf-8") as redeem_file:
        redeem_code = await redeem_file.readlines()

    user_redeem = message.text.split("/redeem", 1)[1].strip()
    approved = False

    for redeem_ue in redeem_code:
        if redeem_ue.strip() == user_redeem:
            approved = True
            await remove_redeem_code(redeem_code, user_redeem)
            break

    if approved:
        async with aiofiles.open(file="plugins/ExtraMod/users/premium.txt", mode="r+", encoding="utf-8") as premium_existed:
            existed_user = await premium_existed.read()
            if str(message.from_user.id) + '\n' not in existed_user:
                async with aiofiles.open("plugins/ExtraMod/users/alredeem.txt", mode="w+", encoding="utf-8") as al_redeem:
                    already = await al_redeem.read()
                    if user_redeem in already:
                        await message.reply("<b>CODE ALREADY REDEEM</b>")
                    else:
                        await message.reply(f"""
<b>NOW YOU ARE A PREMIUM USER</b>                                               
<b>CODE</b>: <code>{user_redeem}</code>                                        
<b>US$</b>: <b>10$<b/>                                      
<b>STATUS</b>: Approved ✅
<b>USERNAME</b>: @{message.from_user.username}
""")
                        await al_redeem.write(user_redeem + '\n')
                        await premium_existed.write(str(message.from_user.id) + '\n')
            else:
                await message.reply('<b>This User Is Already a Premium Member</b>')
    else:
        await message.reply("<b>INVALID REDEEM CODE</b>")
