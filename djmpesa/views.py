from rest_framework.views import APIView
from rest_framework.response import Response
from djmpesa.mpesa_gateway import MpesaPaymentAPI
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from datetime import datetime
from djmpesa.models import *

# Create your views here.
class STKPushAPIView(APIView):
    def post(self, request):
        amount = request.data.get('amount')
        phone_number = request.data.get('phone_number')
        account_number = request.data.get('account_number') #in this case this is a database instance id eg order

        daraja_api = MpesaPaymentAPI()
        response = daraja_api.raise_stk_push(amount, phone_number,account_number)
        narration = f"Payment for  a transaction {account_number}"


        response_code = response.get('ResponseCode')
        merchant_request_id = response.get('MerchantRequestID')
        checkout_request_id = response.get('CheckoutRequestID')
        customer_message = response.get('CustomerMessage')
        response_desc = response.get('ResponseDescription')

        if response_code != "0":

            response_data = {
                "status": 400,
                "message": "Failed to initiate stk push. Try again later",
                'response': response
            }
        else:
            data = {
                "MerchantRequestID":merchant_request_id,
                "CheckoutRequestID": checkout_request_id,
                "ResponseCode": response_code,
                "ResponseDescription": response_desc,
                "CustomerMessage": customer_message,
                "PhoneNumber": phone_number,
                "AccountReference": account_number,
                "TransactionDesc": narration,
                "Amount":amount,
            }
            push_request = STKPushRequest.objects.create(**data)
            push_request.save()

            response_data = {
                "status": 200,
                "message": f"You will receive a prompt to pay KES {amount} for {account_number}", #"Payment requested successfully",
                'response': response
            }


        return Response(response_data)

    

class STKPushCallbackView(CreateAPIView):
    permission_classes = [AllowAny]
    def getTime(self, unformatted_time):
        transation_time = str(unformatted_time)
        transation_date_time = datetime.strptime(transation_time, "%Y%m%d%H%M%S")
        return transation_date_time

    def create(self, request):
        """
        Sample callback
            {
                "Body": {
                    "stkCallback": {
                    "MerchantRequestID": "120326-70411586-1",
                    "CheckoutRequestID": "ws_CO_30052023132032436742415221",
                    "ResultCode": 0,
                    "ResultDesc": "The service request is processed successfully.",
                    "CallbackMetadata": {
                        "Item": [
                        {
                            "Name": "Amount",
                            "Value": 2300
                        },
                        {
                            "Name": "MpesaReceiptNumber",
                            "Value": "LK451H35OP"
                        },
                        {
                            "Name": "Balance"
                        },
                        {
                            "Name": "TransactionDate",
                            "Value": 20171104184944
                        },
                        {
                            "Name": "PhoneNumber",
                            "Value": 254742415221
                        }
                        ]
                    }
                    }
                }
            }
        """

        print('-----------Received M-Pesa webhook----------------------------------------------')

        print("webhook callback data", request.data)

        print('--------------------------------------------------------------------------------')
        data = {}
        data["MerchantRequestID"] = request.data["Body"]["stkCallback"][
            "MerchantRequestID"
        ]
        data["CheckoutRequestID"] = request.data["Body"]["stkCallback"][
            "CheckoutRequestID"
        ]

        data["ResultCode"] = request.data["Body"]["stkCallback"]["ResultCode"]
        data["ResultDesc"] = request.data["Body"]["stkCallback"]["ResultDesc"]

        

        if int(data["ResultCode"]) > 0:
            return Response(data, status=status.HTTP_417_EXPECTATION_FAILED)

        else:
            items = request.data["Body"]["stkCallback"]["CallbackMetadata"]["Item"]

            for item in items:
                data[item.get("Name")] = item.get("Value")


            data["TransactionDate"] = self.getTime(data["TransactionDate"])

            MerchantRequestID = data["MerchantRequestID"]
            CheckoutRequestID = data["CheckoutRequestID"]

            push_request = STKPushRequest.objects.get(
                MerchantRequestID=MerchantRequestID, CheckoutRequestID=CheckoutRequestID
            )
            # get order instance
            
            order_id = push_request.AccountReference
            order = Order.objects.get(id=order_id)

            # update order paid flag
            order.paid = True
            order.save()


            LNMO_instance = LipaNaMPesa.objects.create(**data)

            LNMO_instance.save()
            return Response({"desc": "success"}, status=status.HTTP_200_OK)
        

class BussinessToCustomerAPIView(APIView):
    def post(self, request):
        
        amount = request.data.get("amount")
        phone_number = request.data.get('phone_number')
        remarks = request.data.get('remarks')
        occassion = request.data.get('occassion')

        daraja_api = MpesaPaymentAPI()
        response = daraja_api.business_to_customer(amount, phone_number,remarks, occassion)

        data = {}
        data["CheckoutRequestID"] = response.get("CheckoutRequestID")
        data["OriginatorConversationId"] = response.get("OriginatorConversationId")
        data["ResponseDescription"] = response.get("ResponseDescription")
        data["Amount"] = request["Amount"]
        data["PartyB"] = request["PartyB"]

        withdrawal_request = B2CRequest.objects.create(**data)
        withdrawal_request.save()

        return Response(response.json())


class B2CResultView(CreateAPIView):
    permission_classes = [AllowAny]

    def create(self, request):
        data = {}
        data["ConversationId"] = request.data["Result"]["ConversationId"]
        data["OriginatorConversationId"] = request.data["Result"][
            "OriginatorConversationId"
        ]
        data["ResultDesc"] = request.data["Result"]["ResultDesc"]
        data["ResultType"] = request.data["Result"]["ResultType"]
        data["ResultCode"] = request.data["Result"]["ResultCode"]
        data["TransactionID"] = request.data["Result"]["TransactionID"]

        if int(data["ResultCode"]) > 0:
            return Response(data, status=status.HTTP_417_EXPECTATION_FAILED)

        else:
            items = request.data["Result"]["ResultParameters"]["ResultParameter"]

            for item in items:
                data[item.get("Name")] = item.get("Value")

            data["TransactionCompletedDateTime"] = self.getTime(
                data["TransactionCompletedDateTime"]
            )

            withdrawal_instance = B2CResult.objects.create(**data)

            withdrawal_instance.save()

            return Response({"desc": "success"}, status=status.HTTP_200_OK)


class B2CQueueView(CreateAPIView):    
    def create(self, request):
        data = request.data
        print(f'Queue callback data from daraja')

        response = {
            'data':data
        }
        return Response(response)

