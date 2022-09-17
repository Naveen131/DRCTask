from django.contrib import admin
from .models import User, MobileOtp
# Register your models here.

admin.site.register(User)
admin.site.register(MobileOtp)