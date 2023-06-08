import requests
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64
import os
from dotenv import load_dotenv
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class MpesaC2bCredential:
    consumer_key = os.environ.get('CONSUMER_KEY')
    consumer_secret = os.environ.get('CONSUMER_SECRET')
    api_URL = os.environ.get('API_URL')


class MpesaAccessToken:
    def __init__(self):
        self.r = requests.get(MpesaC2bCredential.api_URL,
                              auth=HTTPBasicAuth(MpesaC2bCredential.consumer_key, MpesaC2bCredential.consumer_secret))
        self.mpesa_access_token = json.loads(self.r.text)
        self.validated_mpesa_access_token = self.mpesa_access_token['access_token']

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None or exc_value is None or traceback is not None:
            return exc_value


class LipanaMpesaPpassword:
    lipa_time = datetime.now().strftime('%Y%m%d%H%M%S')
    Business_short_code = os.environ.get('BUSINESS_SHORT_CODE')
    Test_c2b_shortcode = "600775"
    passkey = os.environ.get('PASSKEY')
    data_to_encode = Business_short_code + passkey + lipa_time
    online_password = base64.b64encode(data_to_encode.encode())
    decode_password = online_password.decode('utf-8')


class PaymentTypes:
    deposits = 1
    share_capital = 2
    loan_application = 3
    loan_payment = 4
