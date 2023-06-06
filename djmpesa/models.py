from django.db import models

# Create your models here.
class STKPushRequest(models.Model):
    MerchantRequestID = models.CharField(max_length=50)
    CheckoutRequestID = models.CharField(max_length=50)
    ResponseCode = models.IntegerField()
    ResponseDescription = models.CharField(max_length=150)
    CustomerMessage = models.CharField(max_length=150)
    AccountReference = models.CharField(max_length=150)
    TransactionDesc = models.CharField(max_length=150)
    PhoneNumber = models.CharField(max_length=150)
    Amount = models.CharField(max_length=150)
    TransactionDate = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Checkout id: {self.CheckoutRequestID} by {self.PhoneNumber}"
    

class LipaNaMPesa(models.Model):
    MerchantRequestID = models.CharField(max_length=50)
    CheckoutRequestID = models.CharField(max_length=50)
    ResultCode = models.IntegerField()
    ResultDesc = models.CharField(max_length=150)
    Amount = models.FloatField()
    MpesaReceiptNumber = models.CharField(max_length=20)
    Balance = models.FloatField(default=0, blank=True, null=True)
    PhoneNumber = models.CharField(max_length=13)
    TransactionDate = models.DateTimeField(auto_now=False, auto_now_add=False)

    def __str__(self):
        return f"{self.PhoneNumber} has sent {self.Amount}. Receipt number: {self.MpesaReceiptNumber}"  
    


class B2CRequest(models.Model):
    ConversationId = models.CharField(max_length=50)
    OriginatorConversationId = models.CharField(max_length=50)
    ResponseDescription = models.CharField(max_length=150)
    Amount = models.BigIntegerField()
    PartyB = models.CharField(max_length=20)
    RequestDateTime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"pay: {self.PartyB} by {self.Amount}"


class B2CResult(models.Model):
    ConversationId = models.CharField(max_length=50)
    OriginatorConversationId = models.CharField(max_length=50)
    ResultDesc = models.CharField(max_length=150)
    ResultType = models.IntegerField()
    ResultCode = models.IntegerField()
    TransactionID = models.CharField(max_length=50)
    ReceiverPartyPublicName = models.CharField(max_length=150)
    TransactionAmount = models.BigIntegerField()
    B2CWorkingAccountAvailableFunds = models.FloatField()
    B2CUtilityAccountAvailableFunds = models.FloatField()
    B2CChargesPaidAccountAvailableFunds = models.FloatField()
    B2CRecipientIsRegisteredCustomer = models.CharField(max_length=1)
    TransactionCompletedDateTime = models.DateTimeField(
        auto_now=False, auto_now_add=False)

    def __str__(self):
        return f"Checkout: {self.TransactionAmount} by {self.B2CRecipientIsRegisteredCustomer}"