from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import User


class UserSerializer(serializers.ModelSerializer):

    first_name = serializers.CharField(min_length=2, max_length=128, required=False)
    last_name = serializers.CharField(min_length=2, max_length=128, required=False)
    email = serializers.CharField(min_length=2, max_length=128, required=False)
    primary_email = serializers.CharField(min_length=2, max_length=128, required=True)
    alternate_email = serializers.CharField(min_length=2, max_length=128, required=False)
    username = serializers.CharField(min_length=2, max_length=128, required=True)
    password = serializers.CharField(min_length=6, max_length=128, required=True)

    class Meta:
        model = User

        fields = ('username','first_name', 'last_name', 'email', 'primary_email',
                  'alternate_email', 'password')

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