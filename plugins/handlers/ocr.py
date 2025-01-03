# Import necessary modules
from pyrogram import filters, Client
from pyrogram.types import Message
import os
import zipfile
from pathlib import Path
import shutil
import requests
import base64
from concurrent.futures import ThreadPoolExecutor
from configparser import ConfigParser
from helpers.timemanager import run_sync_in_thread
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import re


# load Config!
config = ConfigParser()
config.read("config.ini")
api_key = config["GOOGLE"]["VISION_KEY"]


# Function to perform OCR on an image
def ocr_image(image_path, api_key):
    endpoint = "https://vision.googleapis.com/v1/images:annotate"
    headers = {
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip",
        "User-Agent": "FirebaseML_[DEFAULT] Google-API-Java-Client Google-HTTP-Java-Client/1.25.0-SNAPSHOT (gzip)",
        "x-android-package": "com.inverseai.image_to_text_OCR_scannes",
        "x-android-cert": "C9E5C6094C5B966C4DD3C8E65B144622E21AC254",
    }
    params = {"key": api_key}

    with open(image_path, "rb") as image_file:
        image_content = base64.b64encode(image_file.read()).decode("utf-8")

    request_body = {
        "requests": [
            {
                "image": {"content": image_content},
                "features": [{"type": "TEXT_DETECTION"}],
            }
        ]
    }

    response = requests.post(
        endpoint, headers=headers, params=params, json=request_body
    )

    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code)
        print(response.text)
        return None


# Function to process image and save OCR result
def process_image(image_path, output_folder, api_key):
    result = ocr_image(image_path, api_key)
    if result:
        output_path = os.path.join(
            output_folder, os.path.splitext(os.path.basename(image_path))[0] + ".txt"
        )
        with open(output_path, "w", encoding="utf-8") as output_file:
            if "textAnnotations" in result["responses"][0]:
                text = result["responses"][0]["textAnnotations"][0]["description"]
                output_file.write(text.encode("utf-8").decode("utf-8"))
            else:
                output_file.write("Null")


# Function to process images in a folder using multiple threads
@run_sync_in_thread
def process_images_in_folder(input_folder, output_folder, api_key):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with ThreadPoolExecutor(max_workers=25) as executor:
        image_paths = [
            os.path.join(input_folder, filename)
            for filename in os.listdir(input_folder)
            if filename.endswith((".jpg", ".jpeg", ".png", ".PNG"))
        ]
        executor.map(lambda x: process_image(x, output_folder, api_key), image_paths)


# This is Make a Srt
def make_srt(pathname):
    srt_file_list = {}
    subtitle_number = 1  # Initialize subtitle number
    for filename in os.listdir(pathname):
        try:
            start_hour = filename.split("_")[0]
            start_min = filename.split("_")[1]
            start_sec = filename.split("_")[2][:2]
            start_micro = filename.split("_")[3]

            end_hour = filename.split("__")[1].split("_")[0]
            end_min = filename.split("__")[1].split("_")[1]
            end_sec = filename.split("__")[1].split("_")[2][:2]
            end_micro = filename.split("__")[1].split("_")[3]

        except IndexError:
            print(
                f"Error processing {filename}: Filename format is incorrect. Please ensure the correct format is used."
            )
            continue

        start_time = f"{start_hour}:{start_min}:{start_sec},{start_micro}"
        end_time = f"{end_hour}:{end_min}:{end_sec},{end_micro}"

        with open(os.path.join(pathname, filename), "r", encoding="utf-8") as text_file:
            text_content = text_file.read()

        srt_file_list[filename] = [
            f"{subtitle_number}\n",
            f"{start_time} --> {end_time}\n",
            f"{text_content}\n\n",
        ]
        subtitle_number += 1

    with open("output.srt", "w", encoding="utf-8") as srt_file:
        for line in sorted(srt_file_list):
            srt_file.writelines(srt_file_list[line])


# Function to create a zip file with text files
def zip_output(zip_file_name, source_dir):
    with zipfile.ZipFile(zip_file_name, "w") as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                zipf.write(
                    os.path.join(root, file),
                    os.path.relpath(os.path.join(root, file), source_dir),
                )


# single url ocr Func
def ocr_google_vision(image_url, api_key):
    api_endpoint = "https://vision.googleapis.com/v1/images:annotate"
    headers = {"Content-Type": "application/json"}
    params = {"key": api_key}
    payload = {
        "requests": [
            {
                "image": {"source": {"imageUri": image_url}},
                "features": [{"type": "TEXT_DETECTION"}],
            }
        ]
    }

    response = requests.post(api_endpoint, headers=headers, params=params, json=payload)
    if response.status_code == 200:
        result = response.json()
        if "textAnnotations" in result["responses"][0]:
            text = result["responses"][0]["textAnnotations"][0]["description"]
            return text
        else:
            return "No text found in the image."
    else:
        return "Error: {}".format(response.status_code)


# This func for Local Single Photos
@run_sync_in_thread
def ocr_image_single(image_path):
    endpoint = "https://vision.googleapis.com/v1/images:annotate"
    headers = {
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip",
        "User-Agent": "FirebaseML_[DEFAULT] Google-API-Java-Client Google-HTTP-Java-Client/1.25.0-SNAPSHOT (gzip)",
        "x-android-package": "com.inverseai.image_to_text_OCR_scannes",
        "x-android-cert": "C9E5C6094C5B966C4DD3C8E65B144622E21AC254",
    }
    params = {"key": api_key}

    with open(image_path, "rb") as image_file:
        image_content = base64.b64encode(image_file.read()).decode("utf-8")

    request_body = {
        "requests": [
            {
                "image": {"content": image_content},
                "features": [{"type": "TEXT_DETECTION"}],
            }
        ]
    }

    response = requests.post(
        endpoint, headers=headers, params=params, json=request_body
    )

    if response.status_code == 200:
        result = response.json()
        if "textAnnotations" in result["responses"][0]:
            text = result["responses"][0]["textAnnotations"][0]["description"]
            return text
        else:
            return "No text found in the image."
    else:
        return "Error: {}".format(response.status_code)


# Command handler for OCR command
@Client.on_message(
    filters.command("ocr", ["/", "."]) | filters.group | filters.photo | filters.regex(r"ocrdata")
)
async def ocr_command(client, message):
    status = await message.reply_text("<b>⎚ `Processing images...`</b>")
    try:
        images_url = message.text.split()[1].strip()
        if images_url:
            recognized_text = ocr_google_vision(images_url, api_key)
            await status.edit_text(
                f"""
    ```
    {recognized_text}     ```                                
    """
            )
    except (IndexError, AttributeError, ValueError) as err:
        pass
    # if not message.reply_to_message: return await message.reply_text('Please Reply With images.zip')
    if message.photo:
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="📝", callback_data="ocrdata"),
                    InlineKeyboardButton(text="🚫", callback_data="closed"),
                ]
            ]
        )
        await message.reply_photo(photo=message.photo.file_id, reply_markup=buttons)
        await client.delete_messages(
            chat_id=message.chat.id, message_ids=[message.id, status.id]
        )
    elif message.reply_to_message:
        if message.reply_to_message.photo:
            download = await client.download_media(
                message.reply_to_message.photo or message.reply_to_message.document
            )
            recognized_text = await ocr_image_single(image_path=download)
            await status.edit_text(
                f"""
    ```
    {recognized_text}     ```                                
    """
            )
            os.remove(download)
        elif message.reply_to_message.document.file_name.endswith(".zip"):
            name = message.reply_to_message.document.file_name
            # Download the 'images.zip' file from Telegram to the 'download' directory
            download_dir = "imagess"  # Update this to your download directory
            download_path = os.path.join(download_dir, name)
            await message.reply_to_message.download(download_path)

            # Specify the 'download' directory
            download_dir = Path(download_dir)

            # Extract the contents of 'images.zip'
            with zipfile.ZipFile(download_dir / name, "r") as zip_ref:
                zip_ref.extractall(download_dir)

            # Process extracted images and create text files
            input_folder = download_dir
            output_folder = "processed_texts"
            await process_images_in_folder(input_folder, output_folder, api_key)

            # Create a zip file with text files
            output_zip = "processed_texts.zip"
            file_srt = make_srt(pathname=output_folder)
            try:
                await client.send_document(
                    chat_id=message.chat.id, document="output.srt", caption=f"{name}"
                )
            except ValueError as err:
                print(err)

            zip_output(output_zip, output_folder)
            # Upload the zip file to Telegram
            with open(output_zip, "rb") as zip_file:
                await client.send_document(
                    chat_id=message.chat.id, document=zip_file, caption=f"{name}"
                )

            # Clean up: Delete unnecessary files and directories
            shutil.rmtree(download_dir)
            shutil.rmtree(output_folder)
            os.remove("output.srt")
            os.remove(output_zip)

            await status.delete()
        else:
            await status.edit_text(
                "<b><i>Please reply to a message containing an <code>/ocr images.zip</code></i></b>"
            )
    else:
        await status.edit_text(
            "<b><i>Please reply to a message containing an <code>/ocr images.zip</code></i></b>"
        )
