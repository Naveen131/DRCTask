import random
import requests
import json
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.utils import json

from .models import User, MobileOtp


class UserSerializer(serializers.ModelSerializer):

    first_name = serializers.CharField(min_length=2, max_length=128, required=False)
    last_name = serializers.CharField(min_length=2, max_length=128, required=False)
    email = serializers.CharField(min_length=2, max_length=128, required=False)
    primary_email = serializers.CharField(min_length=2, max_length=128, required=True)
    alternate_email = serializers.CharField(min_length=2, max_length=128, required=False)
    username = serializers.CharField(min_length=6, max_length=128, required=True)
    password = serializers.CharField(min_length=6, max_length=128, required=True)
    mobile = serializers.CharField(min_length=10, max_length=12, required=True)


    class Meta:
        model = User

        fields = ('username', 'first_name', 'last_name', 'email', 'primary_email',
                  'alternate_email', 'password', 'mobile')

    def validate(self, attrs):
        EXTRA_FIELDS_IN_PAYLOAD = "Payload contains extra fields"
        errors = {}
        # check extra fields in payload, if found raise an error message
        if hasattr(self, 'initial_data'):
            extra_fields = set(self.initial_data.keys()) - set(self.fields.keys())
            if extra_fields:
                extra_fields = ", ".join(extra_fields)
                errors.setdefault("message", []).append(EXTRA_FIELDS_IN_PAYLOAD.format(extra_fields))

        user = User.objects.filter(username=attrs['username']).exists()
        if user:
            errors.setdefault("username",[]).append("user already exists with this username")

        email = User.objects.filter(primary_email=attrs['primary_email']).exists()

        if email:
            errors.setdefault("email", []).append("user already exists with this email")

        if len(errors) > 0:
            raise ValidationError(errors)

        return attrs


class UserViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class LoginSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField(required=True)
    class Meta:
        model = User
        fields = ("mobile",)

    def validate(self, attrs):
        EXTRA_FIELDS_IN_PAYLOAD = "Payload contains extra fields"
        errors = {}
        # check extra fields in payload, if found raise an error message
        if hasattr(self, 'initial_data'):
            extra_fields = set(self.initial_data.keys()) - set(self.fields.keys())
            if extra_fields:
                extra_fields = ", ".join(extra_fields)
                errors.setdefault("message", []).append(EXTRA_FIELDS_IN_PAYLOAD.format(extra_fields))

        mobile = User.objects.filter(mobile=attrs['mobile']).exists()
        user_obj = self.context['user_obj']

        if user_obj.otp_attempt_time:
            time_diff = timezone.now() - user_obj.otp_attempt_time
            if int(time_diff.seconds/60) <= 5:
                raise ValidationError("User is blocked for {} minutes".format(int(time_diff.seconds/60)))

        if not mobile:
            errors.setdefault("mobile", []).append("user does not exist")

        if len(errors) > 0:
            raise ValidationError(errors)

        return attrs

    def create(self, validated_data, user_obj):
        import string
        from random import choice
        chars = string.digits
        otp = ''.join(choice(chars) for _ in range(4))

        otp_payload = dict(otp=otp, user=user_obj)
        otp_obj = MobileOtp.objects.create(**otp_payload)
        api_key = "x7wpLeb8RWOdF9zHQYgaDCiTynqjJV1U6trshABSu5f43NkEXMvOgPufKjBr73eURzh6NFaCQV8LSJxl"
        # mention url
        url = "https://www.fast2sms.com/dev/bulkV2"

        # create a dictionary
        my_data = {
            # Your default Sender ID
            'sender_id': 'FSTSMS',
            'message': 'Your login OTP is {0}'.format(otp_obj.otp),
            'language': 'english',
            'route': 'p',
            'numbers': user_obj.mobile
        }

        # create a dictionary
        headers = {
            'authorization': api_key,
            'Content-Type': "application/x-www-form-urlencoded",
            'Cache-Control': "no-cache"
        }

        response = requests.request("POST",url,
                                    data=my_data,
                                    headers=headers)
        returned_msg = json.loads(response.text)
        return otp_obj

class MobileOtpSerializer(serializers.ModelSerializer):
    class Meta:
        model = MobileOtp
        fields = "__all__"


class VerifyOtpserializer(serializers.ModelSerializer):
    otp = serializers.CharField(required=True)
    mobile = serializers.CharField(max_length=12)

    class Meta:
        model = MobileOtp
        fields = ('otp','mobile')

    def validate(self, attrs):
        errors = {}
        EXTRA_FIELDS_IN_PAYLOAD = "Payload contains extra fields {}"
        if hasattr(self, 'initial_data'):
            extra_fields = set(self.initial_data.keys()) - set(self.fields.keys())
            if extra_fields:
                extra_fields = ", ".join(extra_fields)
                errors.setdefault("message", []).append(EXTRA_FIELDS_IN_PAYLOAD.format(extra_fields))

        user_obj = User.objects.get(mobile=attrs['mobile'])

        otp = user_obj.otp.all()
        if otp:
            otp = otp.last()
            time_diff = timezone.now() - otp.created_at
            if otp.count >= 3:
                user_obj.otp_attempt_time = timezone.now()
                user_obj.save()
                raise ValidationError("OTP maximum amount attempt reached, "
                                      "user blocked for 5 minutes")

            if time_diff.seconds/60 > 5:
                raise ValidationError("OTP Expired")

            if attrs['otp'] != otp.otp:
                otp.count += 1
                otp.save()
                raise ValidationError("Incorrect OTP")

        if len(errors) > 0:
            raise ValidationError(errors)

        return attrs


