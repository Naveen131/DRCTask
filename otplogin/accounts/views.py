from http.client import BAD_REQUEST
from rest_framework.authtoken.models import Token

from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.utils.serializer_helpers import ReturnList

from .models import User, MobileOtp
from .serializers import UserSerializer, UserViewSerializer, \
    MobileOtpSerializer, LoginSerializer, VerifyOtpserializer


# Create your views here.
class APIResponse(Response):
    """
    An HttpResponse that allows its data to be rendered into
    arbitrary media types.
    """

    def __init__(self, data=None, status=None,
                 template_name=None, headers=None,
                 exception=False, content_type=None):
        """
        Alters the init arguments slightly.
        For example, drop 'template_name', and instead use 'data'.
        Setting 'renderer' and 'media_type' will typically be deferred,
        For example being set automatically by the `APIView`.
        """
        super().__init__(None, status=status)

        if isinstance(data, Serializer):
            msg = (
                'You passed a Serializer instance as data, but '
                'probably meant to pass serialized `.data` or '
                '`.error`. representation.'
            )
            raise AssertionError(msg)

        self.data = data
        self.template_name = template_name
        self.exception = exception
        self.content_type = content_type
        self.status_code = status
        self.errors = None

        if isinstance(data, dict):
            self.errors = data.pop("errors", None)

        if headers:
            for name, value in headers.items():
                self[name] = value

        self.api_status = False
        self.message = "Failed"

        if self.status_code in [200, 201, 204, 208]:
            self.api_status = True
            self.message = "Success"
        elif "message" in self.data and self.status_code not in [200, 201, 208]:
            if isinstance(self.data, dict):
                if isinstance(self.data['message'], str) and "result" not in self.data:
                    self.data = {"message": self.data.values()}

        # validate self.data type is ReturnList object then removed blank set.
        if isinstance(self.data, ReturnList):
            error_list = []
            for error in self.data:
                if len(error) > 0 and self.status_code not in [200, 201, 208]:
                    error_list.append(error)

            if len(error_list) > 0:
                self.data = error_list

        self.data = {'status': self.api_status, 'code': self.status_code, 'message': self.message, 'data': self.data}

        if self.errors is not None:
            if "message" in self.data:
                del self.data['message']

            self.data['errors'] = self.errors


class APIErrorResponse(Response):
    """
    An HttpResponse that allows its data to be rendered into
    arbitrary media types.
    """

    def get_error_message(self):
        if self.status_code == 400:
            return "bad request"
        elif self.status_code == 404:
            return "resource not found"
        else:
            return "unexpected error"

    def __init__(self, message=None, data=None, status=None, extra_info=None, info=None):
        """
        Alters the init arguments slightly.
        For example, drop 'template_name', and instead use 'data'.
        Setting 'renderer' and 'media_type' will typically be deferred,
        For example being set automatically by the `APIView`.
        """
        super().__init__(None, status=status)

        if extra_info is None:
            extra_info = {}
        if isinstance(data, Serializer):
            msg = (
                'You passed a Serializer instance as data, but '
                'probably meant to pass serialized `.data` or '
                '`.error`. representation.'
            )
            raise AssertionError(msg)

        if data is None:
            data = {}

        self.detail = data
        self.status_code = status
        self.api_status = False
        self.message = "Failed"
        self.data = {'status': self.api_status, 'code': self.status_code, 'message': self.message, 'data': {}}
        # if info is not None:
        #     info = {"url": DOCUMENT_HELP_LINK, "type": DOCUMENT_URL_TYPE}

        if self.status_code in [200, 201, 208]:
            pass
        else:
            if message is None:
                message = self.get_error_message()

            self.data['data'] = dict(code="", message=message, details=self.detail, info=[info])

            if "payload_code" in extra_info:
                self.data['data']['code'] = extra_info['payload_code']


class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return APIErrorResponse(data=serializer.errors, message=BAD_REQUEST,
                                    status=HTTP_400_BAD_REQUEST
                                    )
        try:
            instance = serializer.create(serializer.validated_data)

        except Exception as err:
            return APIErrorResponse(message=err.args[0], status=HTTP_400_BAD_REQUEST,

                                    )

        response = UserViewSerializer(instance).data
        # from django.core.mail import send_mail
        # # template = "templates/user_registration.html"
        # # template = Template(mark_safe(template))
        # # context = Context({'data': instance})
        # # template = template.render(context)
        # from django.template.loader import render_to_string
        # html_code = render_to_string("user_registration.html", data)
        #
        # send_mail(
        #     'Forgot your password',
        #     'Here is the message.',
        #     'naveen.c131@gmail.com',
        #     [instance.email],
        #     fail_silently=False,
        #     html_message=html_code
        # )

        return APIResponse(data, 200)


class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)
    queryset = User.objects.all()

    def get_object(self, mobile):
        user_obj = User.objects.get(mobile=mobile)
        return user_obj

    def post(self, request, *args, **kwargs):

        user_obj = self.get_object(request.data['mobile'])
        serializer = self.serializer_class(data=request.data,
                                           context={"user_obj": user_obj})

        if not serializer.is_valid():
            return APIErrorResponse(data=serializer.errors, message=BAD_REQUEST,
                                    status=HTTP_400_BAD_REQUEST
                                    )
        try:
            instance = serializer.create(serializer.validated_data, user_obj)

        except Exception as err:
            return APIErrorResponse(message=err.args[0], status=HTTP_400_BAD_REQUEST,)
        response = MobileOtpSerializer(instance).data
        return APIResponse(response, 200)


class VerifyOtpView(generics.RetrieveAPIView):
    queryset = MobileOtp.objects.all()
    serializer_class = VerifyOtpserializer
    permission_classes = (AllowAny,)

    def check_otp(self, validated_data):

        user_obj = User.objects.get(mobile=validated_data['mobile'])

        otp = user_obj.otp.all().last()
        if validated_data['otp'] == otp.otp:
            user_obj.otp_attempt_time = None
            user_obj.save()
            return True, user_obj
        return False, user_obj

    def post(self, request, *args, **kwargs):
        data = request.data

        serializer = self.serializer_class(data=data)

        if not serializer.is_valid():
            return APIErrorResponse(data=serializer.errors, message=BAD_REQUEST,
                                    status=HTTP_400_BAD_REQUEST
                                    )

        validated_data = serializer.validated_data
        try:
            resp, user_obj = self.check_otp(data)

        except Exception as err:
            return APIErrorResponse(message=err.args[0], status=HTTP_400_BAD_REQUEST)

        if not resp:
            data = {"message": "Invalid OTP"}
        else:
            token = Token.objects.create(user=user_obj)
            data = {"message": "success", "token": token.key}

        return APIResponse(data, 200)
