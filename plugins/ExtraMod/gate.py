import requests
from bs4 import BeautifulSoup
import re
from fake_useragent import UserAgent
from pyrogram import Client, filters
from pyrogram.types import Message



# This is a handleer
@Client.on_message(filters.command('gate', ['/', '.']))
async def gate(bot: Client, cmd: Message):
    global status
    status = await cmd.reply_text("<b>⎚ `Bypassing...`</b>")
    if cmd.reply_to_message:
        url = cmd.reply_to_message.text
        await process_url(cmd, url)
    elif cmd.text:
        try:
            _, url = cmd.text.split()
        except Exception:
            await status.edit_text('<b>Please Reply With site or Command</b>')
        else:
            await process_url(cmd, url)
    else:
        await status.edit_text('<b>Please Reply With site or Command</b>')


# This is func for User Agent
def get_random_user_agent():
    ua = UserAgent()
    return ua.random


# This is For Check GateWay
def check_gateway(url):
    try:
        headers = {'User-Agent': get_random_user_agent()}
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error accessing {url}: {e}")
        return None
    bsoup = BeautifulSoup(response.text, 'html.parser')
    payment_gateways = {
        'stripe': ['script', {'src': re.compile(r'.*js\.stripe\.com.*')}, {'src': re.compile(r'.*stripe.*')}],
        'paypal': ['script', {'src': re.compile(r'.*paypal.*')}, {'src': re.compile(r'.*checkout\.paypal\.com.*')}, {'src': re.compile(r'.*paypalobjects.*')}],
        'braintree': ['script', {'src': re.compile(r'.*braintree.*')}, {'src': re.compile(r'.*braintreegateway.*')}],
        'worldpay': ['script', {'src': re.compile(r'.*worldpay.*')}],
        'authnet': ['script', {'src': re.compile(r'.*authorizenet.*')}, {'src': re.compile(r'.*authorize\.net.*')}],
        'recurly': ['script', {'src': re.compile(r'.*recurly.*')}],
        'shopify': ['script', {'src': re.compile(r'.*shopify.*')}],
        'square': ['script', {'src': re.compile(r'.*square.*')}],
        'cybersource': ['script', {'src': re.compile(r'.*cybersource.*')}],
        'adyen': ['script', {'src': re.compile(r'.*adyen.*')}],
        '2checkout': ['script', {'src': re.compile(r'.*2checkout.*')}],
        'authorize.net': ['script', {'src': re.compile(r'.*authorize\.net.*')}],
        'worldpay': ['script', {'src': re.compile(r'.*worldpay.*')}],
        'eway': ['script', {'src': re.compile(r'.*eway.*')}],
        'bluepay': ['script', {'src': re.compile(r'.*bluepay.*')}],
    }

    detected_gateway = None

    for pg, patterns in payment_gateways.items():
        script_elements = bsoup.find_all(
            'script', {'src': patterns[1]['src']}) if len(patterns) > 1 else []
        script_elements += bsoup.find_all(
            'script', {'src': patterns[2]['src']}) if len(patterns) > 2 else []
        script_elements += bsoup.find_all(
            'script', {'src': patterns[3]['src']}) if len(patterns) > 3 else []

        if bsoup.find(*patterns) or any(script_element for script_element in script_elements) or bsoup.find(string=re.compile(rf'.*{pg}.*', re.IGNORECASE)):
            detected_gateway = pg
            break

    return url, detected_gateway


def add_https_if_missing(url):
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'https://' + url
    return url


async def send_message(cmd, url, gateway):
    if gateway:
        msg = f'🔗 **Url:** <code>[{url}]({url})</code>\n🌐 **Gateway:** <code>{gateway}</code>'
        await status.edit_text(msg)
    else:
        await status.edit_text('<b>No Gateway Found!</b>')


async def process_url(cmd, url):
    url = url.strip()
    url = add_https_if_missing(url)
    try:
        result = check_gateway(url)
        if result[1] is None:
            return await status.edit_text('<b>No Gateway Found!</b>')
        if result and result[1]:
            url, gateway = result
            await send_message(cmd, url, gateway)
    except Exception as e:
        await status.edit_text(e)
        print(f"Error processing {url}: {e}")

"""async def main(cmd, urls):
    workers = min(10, len(urls))
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        executor.map(process_url,cmd, urls)"""

"""if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Execution time: {end_time - start_time} seconds")
"""
