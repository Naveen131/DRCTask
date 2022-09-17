from django.urls import path
from .views import UserRegisterView, LoginView, VerifyOtpView

urlpatterns = [
    path('api/v1/add-user', UserRegisterView.as_view(), name='add-user'),
    path('api/v1/send-otp', LoginView.as_view(), name='send-otp'),
    path('api/v1/verify-otp', VerifyOtpView.as_view(), name='verify-otp')
]
