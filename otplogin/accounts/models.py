from datetime import datetime

from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser

from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, primary_email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not primary_email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(primary_email)
        user = self.model(primary_email=primary_email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, primary_email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(primary_email, password, **extra_fields)

    def create_superuser(self, primary_email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(primary_email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField('username', max_length=30, unique=True)
    primary_email = models.EmailField('email address', unique=True)
    alternate_email = models.EmailField('alternate email', blank=True)
    first_name = models.CharField('first name', max_length=30, blank=True)
    last_name = models.CharField('last name', max_length=30, blank=True)
    is_active = models.BooleanField('active', default=True)
    is_staff = models.BooleanField('staff', default=True)

    objects = UserManager()

    USERNAME_FIELD = 'primary_email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'auth_user'
        permissions = [('list_user', 'Can list auth user')]

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs)


class MobileOtp(models.Model):
    mobile = models.CharField(max_length=20)
    otp = models.CharField(max_length=6)
    user = models.ForeignKey(User, related_name='otp', on_delete=models.CASCADE)
    count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=datetime.now())