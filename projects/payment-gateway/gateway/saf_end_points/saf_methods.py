import json

import requests
from flask import jsonify
from gateway.mpesa_credentials import MpesaAccessToken, LipanaMpesaPpassword


class SafMethods:

    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def send_push(self, **kwargs):
        try:
            # tx_ref = kwargs['uiid']+kwargs['member_number']
            with MpesaAccessToken() as mpesa_token:
                access_token = mpesa_token.validated_mpesa_access_token
            amount = 0
            lines = kwargs['args']
            if type(lines) is list:
                for line in lines:
                    amount += line['amount']
            else:
                amount = lines
            request_body = {
                "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
                "Password": LipanaMpesaPpassword.decode_password,
                "Timestamp": LipanaMpesaPpassword.lipa_time,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": amount,
                # replace with your phone number to get stk push
                "PartyA": kwargs['phone_number'],
                "PartyB": LipanaMpesaPpassword.Business_short_code,
                # replace with your phone number to get stk push
                "PhoneNumber": kwargs['phone_number'],
                "CallBackURL": "https://api-mobile-money.tritel.co.ke/api/v1/c2b/callback",
                "AccountReference": "%s" % kwargs['uiid'],
                "TransactionDesc": "%s" % kwargs['uiid']
            }
            api_url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
            headers = {"Authorization": "Bearer %s" % access_token}
            response = requests.post(
                api_url, json=request_body, headers=headers)
            print(response)
            return response.text
        except Exception as e:
            print(e)
            return str(e)

    def send_money(self, args):
        pass

    def reverse(self, args):
        pass

    def transaction_status(self, args):
        pass

    def get_token(self):
        pass

    def register_url(self):
        with MpesaAccessToken() as mpesa_token:
            mpesa_token = MpesaAccessToken.validated_mpesa_access_token
            args = {
                "ShortCode": LipanaMpesaPpassword.Business_short_code,
                "ResponseType": "Canceled",
                "ConfirmationURL": "https://api-mobile-money.tritel.co.ke/api/confirmationCallback",
                "ValidationURL": "https://api-mobile-money.tritel.co.ke/api/validationResponse"
            }
            api_url = "https://api.safaricom.co.ke/mpesa/c2b/v1/registerurl"
            headers = {"Authorization": "Bearer %s" % mpesa_token}
            response = requests.post(api_url, json=args, headers=headers)
            print(json.dumps(response.json(), ensure_ascii=False))
            return json.dumps(response.json(), ensure_ascii=False)

    # def make_payment(self):
    #     with MpesaAccessToken() as mpesa_token:
    #         mpesa_token = MpesaAccessToken.validated_mpesa_access_token
    #         args = {
    #             "ShortCode": LipanaMpesaPpassword.Business_short_code,
    #             "CommandID": "CustomerPayBillOnline",
    #             "Amount": 1,
    #             "Msisdn": 254727292911,
    #             "BillRefNumber": "C2B working"
    #         }
    #         api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/simulate"
    #         headers = {"Authorization": "Bearer %s" % mpesa_token}
    #         response = requests.post(api_url, json=args, headers=headers)
    #         return response
