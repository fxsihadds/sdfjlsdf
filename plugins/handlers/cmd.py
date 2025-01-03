from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
import wget
import requests as re
import os, asyncio, time
from ..extra.temp import buttons_l, msg_buttons
from ..handlers.rnd import regenerate_callback
from helpers.forcesub import ForceSub
from database.mongodbs import adduser, is_exsist
from ..handlers.ocr import ocr_image_single
from helpers._ocr_helpers import sub_images
from helpers.video_meta_data import META
from helpers.display_progress import progress_for_pyrogram
from ..handlers.testline import find_strings_from_txt
from pprint import pformat
from ..handlers.Translate_gpt import Translate_text
from pyrogram.errors import MessageNotModified  # Import the MessageNotModified error

# Define the InlineKeyboardMarkup
_cmd_button = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("Tool", callback_data="tool"),
            InlineKeyboardButton("Checkers", callback_data="checkers"),
            InlineKeyboardButton("Gates", callback_data="gates"),
        ],
        [
            InlineKeyboardButton("Admin", callback_data="admin"),
            InlineKeyboardButton("Close", callback_data="closed"),
        ],
    ]
)

tools_Click = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("Checkers", callback_data="checkers"),
            InlineKeyboardButton("Gates", callback_data="gates"),
            InlineKeyboardButton("Others", callback_data="others"),
        ],
        [
            InlineKeyboardButton("Admin", callback_data="admin"),
            InlineKeyboardButton("Close", callback_data="closed"),
        ],
    ]
)


buttons = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("Generate", callback_data="generate"),
            InlineKeyboardButton("Refresh", callback_data="refresh"),
            InlineKeyboardButton("Close", callback_data="close"),
        ]
    ]
)


tools = """<i>Available commands:</i>
`.gscr` - `Extract email:pass`
`.uscr` - `Extract user:pass, number:pass`
`.paste` - `paste any text`
`.unzip` - `unzip a file`
`.ip` - `check your ip address`
`.rand` - `generate random details`
`.bomb` - `send prank messages to a friend`
`.temp` - `create a temporary email`
`.txt` - `create a text file`
`.nid` - `work with nid deals`
`.surl` - `create a short url`
"""

checkers = """<i>Available commands:</i>
`.hoi` - `validate hoichoi combo`
`.crun` - `validate crunchyroll combo`
`.chaupal` - `validate chaupal combo`
`.chor` - `validate chorki combo`

"""


others = """<i>Available commands:</i>
`.bin` - `validate bin`
`.bypass` - `bypass shortened urls`
`.remv` - `remove background from a photo`
`.gemi` - `use google ai for images and text`
`.genimg` - `generate an image`
`.gpt` - `translate text`
`.dl` - `download telegram-restricted videos`
`.redeem` - `purchase premium access`

"""
Gates = """<i>Available commands:</i>
`.vbv` - `check your 3ds card (vbv)`
`.3ds` - `validate your 3ds card`
`.b3` - `perform braintree authentication`
`.chk` - `remove background from a photo`
`.auth` - `use google ai for image and text processing`
`.ayden` - `purchase premium access`

"""


admin = """<i>Available commands:</i>
`.register` - `add a user`
`.unregister` - `remove a user`
`.userlist` - `display the list of users`
`.restart` - `restart the program`
`.speedtest` - `test server speed`
"""


@Client.on_message(filters.command(["help", "start"]) & filters.incoming)
async def help_command(Client, message):
    user_id = message.from_user.id
    # force_sub = await ForceSub(Client, message)
    is_exsists = is_exsist(user_id)
    # if force_sub == 400: return
    if not is_exsists:
        await message.reply_text("<code>𝖈𝖔𝖒𝖒𝖆𝖓𝖉𝖘: </code>", reply_markup=_cmd_button)
        adduser(bot=Client, cmd=message)
    else:
        await message.reply_text("<code>𝖈𝖔𝖒𝖒𝖆𝖓𝖉𝖘: </code>", reply_markup=_cmd_button)
    global main_admin
    with open(
        file="plugins/ExtraMod/users/admin.txt", mode="r+", encoding="utf-8"
    ) as admin:
        main_admin = admin.readlines()


email = ""


@Client.on_callback_query()
async def cmd(client, callback_query):
    response = callback_query.data
    message = callback_query.message
    try:
        if response == "tool" and callback_query.message.text != f"{tools}\n":
            await callback_query.edit_message_text(
                f"{tools}\n", reply_markup=tools_Click
            )

        elif response == "checkers" and callback_query.message.text != f"{checkers}\n":
            await callback_query.edit_message_text(
                f"{checkers}\n", reply_markup=_cmd_button
            )

        elif response == "others" and callback_query.message.text != f"{others}\n":
            await callback_query.edit_message_text(
                f"{others}\n", reply_markup=_cmd_button
            )
        elif response == "gates" and callback_query.message.text != f"{Gates}\n":
            await callback_query.edit_message_text(
                f"{Gates}\n", reply_markup=_cmd_button
            )
        elif response == "admin" and callback_query.message.text != f"{admin}\n":
            await callback_query.edit_message_text(
                f"{admin}\n", reply_markup=_cmd_button
            )
        elif response == "back" and callback_query.message.text != f"{admin}\n":
            await callback_query.edit_message_text(
                f"{admin}\n", reply_markup=_cmd_button
            )
        elif response == "closed":
            await callback_query.message.delete()
        elif response == "NewGenerate":
            await callback_query.edit_message_text("here are our Main Gmail!")

        elif response == "extract":
            ocr_images_store = f"ocrdict{callback_query.from_user.id}"
            status = await callback_query.message.reply_text(
                "<b>⎚ `Downloading...`</b>"
            )
            download = await client.download_media(message.video)
            await sub_images(
                client, status, download, ocr_images_store
            )  # Ensure to await here
            os.remove(download)
        elif response == "metadata":
            status = await callback_query.message.reply_text(
                "<b>⎚ `Downloading...`</b>"
            )
            video_path = await client.download_media(callback_query.message.video)
            v1 = META(path=video_path)
            result = v1.mediainfo_ext()

            # Format the output for easy copying
            formatted_result = pformat(result, indent=4, width=80)
            await status.edit_text(
                f"<b>Video Information:</b>\n<pre>{formatted_result}</pre>"
            )
            os.remove(video_path)
        elif response == "extaudio":
            status = await callback_query.message.reply_text(
                "<b>⎚ `Downloading...`</b>"
            )
            video_path = await client.download_media(message.video)
            v1 = META(path=video_path)
            result = v1.ext_audio()
            send = await client.send_document(
                chat_id=message.chat.id,
                document="audio/output_audio.mp3",  # Path to the file
                caption="Here is your audio file!",  # Optional caption
            )
            await status.delete()
            os.remove("audio/output_audio.mp3")
            os.remove(video_path)
        elif response == "spvideo":
            status = await callback_query.message.reply_text(
                "<b>⎚ `Downloading...`</b>"
            )
            video_path = await client.download_media(message.video)
            v1 = META(path=video_path)
            result = v1.split_video("output_part1.mp4", "output_part2.mp4")
            part_of_video = ["output_part1.mp4", "output_part2.mp4"]
            # Assuming 'part_of_video' contains a list of file paths for the split video parts
            for idx, items in enumerate(part_of_video):
                # Send each video part
                send = await client.send_video(
                    chat_id=message.chat.id,  # Target chat
                    video=items,  # Path to the video file
                    caption=f"Here is your Video Part {idx + 1}!",  # Caption with part number
                )
                os.remove(items)

            await status.delete()
            os.remove(video_path)
        elif response == "ocrdata":
            if message.photo:
                file_path = await client.download_media(message.photo)
                recognized_text = await ocr_image_single(file_path)
                await callback_query.message.reply_text(recognized_text)
                os.remove(file_path)
                # await asyncio.sleep(2)
                await client.delete_messages(
                    chat_id=message.chat.id, message_ids=[message.id]
                )
            else:
                await callback_query.message.reply_text("No photo to process.")
        elif response == "gentr":
            await Translate_text(client, callback_query)
            """text = await message.text
            await message.reply_text("This is An Text", text)
            return await message.reply_text("Futures Will be Available!")"""

        elif response == "about_gmail":
            await callback_query.edit_message_text("About Gmail!")
        elif response == "ulpextract":
            STATUS_ID = "<b>⎚ `Downloading The Text File...`</b>"
            start_time = time.time()
            file_name = message.document.file_name
            user_folder = f"downloads/{callback_query.from_user.id}"
            file_path = os.path.join(user_folder, file_name)
            if not os.path.exists(user_folder):
                os.makedirs(user_folder)

            user_res = await client.ask(message.chat.id, "WRITE YOUR KEYWORD:✍")
            # Extract the text of the response
            find_str = user_res.text
            status = await message.reply_text("<b>⎚ `Processing...`</b>")
            await message.download(
                file_name=file_path,
                progress=progress_for_pyrogram,
                progress_args=(STATUS_ID, status, file_name, start_time),
            )
            await find_strings_from_txt(find_str, file_path, status, client)
            os.remove(file_path)
            # await callback_query.message.reply_text(f"Thank you, {user_name}!")
        elif response == "trimvideo":
            # trim_video = "video"
            user_res = await client.ask(
                message.chat.id, "Write Your Second Start:end :✍"
            )
            find_str = user_res.text.split(":")
            print(find_str[0], find_str[1])
            video_path = await client.download_media(message.video)
            output_path = os.path.splitext(video_path)[0] + "_trimmed.mp4"
            v1 = META(path=video_path)
            result = v1.trim_video(output_path, int(find_str[0]), int(find_str[1]))
            send = await client.send_video(
                chat_id=message.chat.id,  # Target chat
                video=output_path,  # Path to the video file
                caption=f"Here is your Trim Video",  # Caption with part number
            )
            os.remove(output_path)
            os.remove(video_path)

        elif response == "generatetemp":
            global email
            email = re.get(
                "https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1"
            ).json()[0]
            await callback_query.edit_message_text(
                "__**Your Temporary E-mail: **__`" + str(email) + "`",
                reply_markup=buttons_l,
            )

        elif response == "refreshtemp":
            try:
                if email == "":
                    await callback_query.edit_message_text(
                        "Generate an email", reply_markup=buttons_l
                    )
                else:
                    getmsg_endp = (
                        "https://www.1secmail.com/api/v1/?action=getMessages&login="
                        + email[: email.find("@")]
                        + "&domain="
                        + email[email.find("@") + 1 :]
                    )
                    print(getmsg_endp)
                    ref_response = re.get(getmsg_endp).json()
                    global idnum
                    idnum = str(ref_response[0]["id"])
                    from_msg = ref_response[0]["from"]
                    subject = ref_response[0]["subject"]
                    refreshrply = (
                        "You have a message from "
                        + from_msg
                        + "\n\nSubject : "
                        + subject
                    )
                    await cmd.edit_text(refreshrply, reply_markup=msg_buttons)
            except:
                await callback_query.answer(
                    "No messages were received..\nin your Mailbox " + email,
                    show_alert=True,
                )
        elif response == "view_msgtemp":
            msg = re.get(
                "https://www.1secmail.com/api/v1/?action=readMessage&login="
                + email[: email.find("@")]
                + "&domain="
                + email[email.find("@") + 1 :]
                + "&id="
                + idnum
            ).json()
            print(msg)
            from_mail = msg["from"]
            date = msg["date"]
            subjectt = msg["subject"]
            try:
                attachments = msg["attachments"][0]
            except:
                pass
            body = msg["body"]
            mailbox_view = (
                "ID No : "
                + idnum
                + "\nFrom : "
                + from_mail
                + "\nDate : "
                + date
                + "\nSubject : "
                + subjectt
                + "\nmessage : \n"
                + body
            )
            await callback_query.edit_message_text(mailbox_view, reply_markup=buttons_l)
            mailbox_view = (
                "ID No : "
                + idnum
                + "\nFrom : "
                + from_mail
                + "\nDate : "
                + date
                + "\nSubject : "
                + subjectt
                + "\nmessage : \n"
                + body
            )
            if attachments == "[]":
                await callback_query.edit_message_text(
                    mailbox_view, reply_markup=buttons_l
                )
                await callback_query.answer(
                    "No Messages Were Received..", show_alert=True
                )
            else:
                dlattach = attachments["filename"]
                attc = (
                    "https://www.1secmail.com/api/v1/?action=download&login="
                    + email[: email.find("@")]
                    + "&domain="
                    + email[email.find("@") + 1 :]
                    + "&id="
                    + idnum
                    + "&file="
                    + dlattach
                )
                print(attc)
                mailbox_vieww = (
                    "ID No : "
                    + idnum
                    + "\nFrom : "
                    + from_mail
                    + "\nDate : "
                    + date
                    + "\nSubject : "
                    + subjectt
                    + "\nmessage : \n"
                    + body
                    + "\n\n"
                    + "[Download]("
                    + attc
                    + ") Attachments"
                )
                filedl = wget.download(attc)
                await callback_query.edit_message_text(
                    mailbox_vieww, reply_markup=buttons_l
                )
                os.remove(dlattach)
        elif response == "closetemp":
            await callback_query.edit_message_text("Session Closed✅")
        elif response == "regenerateadds":
            await regenerate_callback(client, callback_query)
    except MessageNotModified:
        await callback_query.answer("Click Another Button!..")
    except Exception as e:
        print(f"An error occurred: {e}")
