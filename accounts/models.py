from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

import uuid 

from accounts.managers import MyAccountManager


class Account(AbstractBaseUser, PermissionsMixin):
    

    class Gender(models.TextChoices):
        MALE = "Male", "Male"
        FEMALE = "Female", "Female"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(verbose_name="email", max_length=60)
    username = models.CharField(verbose_name="username", max_length=30, unique=True)
    fname = models.CharField(verbose_name="first_name", max_length=30)
    lname = models.CharField(verbose_name="last_name", max_length=30)
    gender = models.CharField(
        verbose_name="gender", choices=Gender.choices, max_length=10
    )
    forget_password_token = models.UUIDField(
        verbose_name="forget_password_token", default=None, unique=True, null=True
    )
    date_joined = models.DateTimeField(verbose_name="date_joined", auto_now_add=True)
    last_login = models.DateTimeField(verbose_name="last_login", auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    USERNAME_FIELD = "username"
    objects = MyAccountManager()

    def __str__(self):
        return self.username
