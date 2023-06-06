from django.urls import path
from djmpesa.views import *

urlpatterns = [
    path('stk-pay/', STKPushAPIView.as_view(), name='stk_push'),
    path('epress-payments', STKPushCallbackView.as_view() ,name='stk_callback'),
    path('withdraw/', BussinessToCustomerAPIView.as_view() ,name='b2c'),
    path('withdraw-result', B2CResultView.as_view() ,name='b2c_result'),
    path('queue', B2CQueueView.as_view() ,name='b2c_result'),
]