from pyrogram.types import Message
from pyrogram import Client, filters, enums



async def admin_check(cmd: Message) -> bool:
    if not cmd.from_user: return False
    if cmd.chat.type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]: return False
    #if message.from_user.id in [777000, 1087968824]: return True
    client = cmd._client
    chat_id = cmd.chat.id
    user_id = cmd.from_user.id
    check_status = await client.get_chat_member(chat_id=chat_id,user_id=user_id)
    admin_strings = [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]
    if check_status.status not in admin_strings: return False
    else: return True

async def admin_filter(_, Client, message):
    return await admin_check(message)