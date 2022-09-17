from django.urls import path
from .views import UserRegisterView

urlpatterns = [
    path('api/v1/add-user', UserRegisterView.as_view(), name='add-user'),

]
