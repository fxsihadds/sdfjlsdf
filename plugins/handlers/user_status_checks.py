from pyrogram import Client, filters
from pyrogram.types import Message
from helpers.User_Control import Subscription, subs_button


@Client.on_message(filters.command("info", ["/", "."]))
async def rand_helper_command(_, cmd: Message):
    sub = Subscription(cmd.from_user.id)
    sub_info = sub.get_subscription_info()
    msg = f"""
<b>Subscription Activated!</b>
<b>User ID</b>: {cmd.from_user.id}
Plan: {sub_info.get('plan', 'N/A')}
Start Date: {sub_info.get('start_date', 'N/A')}
End Date: {sub_info.get('end_date', 'N/A')}
Status: {sub_info.get('status', 'N/A')}
"""
    await cmd.reply_text(msg, reply_markup=subs_button)
