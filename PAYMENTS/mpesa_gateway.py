import requests
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64
from django.conf import settings

"""
M-PESA: It is a mobile money transfer service in Kenya that allows users to store and transfer money through their mobile phones.

Command IDs: This is a unique command that specifies transaction types.

Salary Payment: This supports sending money to both registered and unregistered M-Pesa customers.

Business Payment: This is a normal business to customer payment, supports only M-Pesa registered customers.

Promotion Payment: This is a promotional payment to customers. The M-Pesa notification message is a congratulatory message. Supports only M-Pesa registered customers.

Short Code: A short code is the unique number that is allocated to a pay bill or buy goods organization through they will be able to receive customer payment. It could be a Pay bill, Buy Goods or Till Number.

Pay Bill: it is a cash collection service that allows your organization to collect money on a regular basis from your customers through M-PESA.

Buy Goods:  It is mostly for retail purchase of goods and services. Both parties immediately confirm these proximity payments via text message. No relationship between the buyer and the organization or account number is required.

Till Number: Till number is attached to the store number. This is used to make payments by customers.


"""

class MpesaCredential:
    """
    Includes the consumer key, secret and api url either live or sandbox
    """
    consumer_key = 'cHnkwYIgBbrxlgBoneczmIJFXVm0oHky'
    consumer_secret = '2nHEyWSD4VjpNh2g'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'


class MpesaAccessToken:
    """
    Send a get request to daraja api to get an access toke
    """
    r = requests.get(MpesaCredential.api_URL,
                     auth=HTTPBasicAuth(MpesaCredential.consumer_key, MpesaCredential.consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token['access_token']

class MpesaPpassword:
    """
    Generate a password to be used with the daraja APIs
    This is the password used for encrypting the request sent: 
    A base64 encoded string. 
    (The base64 string is a combination of Shortcode+Passkey+Timestamp)
    """
    lipa_time = datetime.now().strftime('%Y%m%d%H%M%S')
    Business_short_code = "174379"
    Test_c2b_shortcode = "600344"
    passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'

    data_to_encode = Business_short_code + passkey + lipa_time

    online_password = base64.b64encode(data_to_encode.encode())
    decode_password = online_password.decode('utf-8')    


class MpesaPaymentAPI:

    """
    A simpler object implementation
    """
    def __init__(self):
        self.base_url = 'https://sandbox.safaricom.co.ke'
        self.consumer_key = settings.DARAJA_CONSUMER_KEY
        self.consumer_secret = settings.DARAJA_CONSUMER_SECRET

    def get_access_token(self):
        api_url = f'{self.base_url}/oauth/v1/generate?grant_type=client_credentials'
        auth_string = f'{self.consumer_key}:{self.consumer_secret}'
        encoded_auth_string = base64.b64encode(auth_string.encode()).decode()

        headers = {
            'Authorization': f'Basic {encoded_auth_string}',
            'Content-Type': 'application/json'
        }

        response = requests.get(api_url, headers=headers)
        access_token = response.json().get('access_token')
        return access_token

    def generate_password(self, business_short_code, passkey, timestamp):
        data = f'{business_short_code}{passkey}{timestamp}'
        encoded_data = base64.b64encode(data.encode()).decode()
        return encoded_data

    def raise_stk_push(self, amount, phone_number,account_number):
        business_short_code = settings.DARAJA_BUSINESS_SHORTCODE
        passkey = settings.DARAJA_PASSKEY
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

        access_token = self.get_access_token()
        password = self.generate_password(business_short_code, passkey, timestamp)
        narration = f"Payment for  a transaction {account_number}"


        api_url = f'{self.base_url}/mpesa/stkpush/v1/processrequest'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        payload = {
            'BusinessShortCode': business_short_code,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': amount,
            'PartyA': phone_number,
            'PartyB': business_short_code,
            'PhoneNumber': phone_number,
            'CallBackURL': 'https://mydomain.com/callback', # Webhook to receive transaction notifications
            'AccountReference': account_number,
            'TransactionDesc': narration
        }


        """
        Sample response
        {
            "MerchantRequestID": "12133-97180190-1",
            "CheckoutRequestID": "ws_CO_06062023111643535708374149",
            "ResponseCode": "0",
            "ResponseDescription": "Success. Request accepted for processing",
            "CustomerMessage": "Success. Request accepted for processing"
        }
        """    
        response = requests.post(api_url, json=payload, headers=headers)
        return response.json()    
    

    def business_to_customer(self, amount, phone_number,account_number, remarks, occassion):
        business_short_code = settings.DARAJA_BUSINESS_SHORTCODE
        passkey = settings.DARAJA_PASSKEY
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

        access_token = self.get_access_token()
        password = self.generate_password(business_short_code, passkey, timestamp)
        narration = f"Payment for  a transaction {account_number}"


        api_url = f'{self.base_url}/mpesa/stkpush/v1/processrequest'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        payload ={
            "InitiatorName": "testapi", #The username of the M-Pesa B2C account API operator.
            "SecurityCredential": password,
            "CommandID": "SalaryPayment", #BusinessPayment, PromotionPayment 
            "Amount": amount,
            "PartyA": business_short_code,
            "PartyB": phone_number,
            "Remarks": remarks,
            "QueueTimeOutURL": "https://mydomain.com/b2c/queue", # Webhook to receive failed transaction notification
            "ResultURL": "https://mydomain.com/b2c/result", # Webhook to receive successful transaction notification
            "Occassion": occassion #Additional information of the transaction
        }

        """
        Sample response
        {
            "ConversationID": "AG_20230606_20101bd12191dba144e4",
            "OriginatorConversationID": "129082-96727437-1",
            "ResponseCode": "0",
            "ResponseDescription": "Accept the service request successfully."
        }
        """

        response = requests.post(api_url, json=payload, headers=headers)
        return response.json()    