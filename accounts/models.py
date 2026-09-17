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
    send_monthly_report = models.BooleanField(default=False)
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


class WebAuthnCredential(models.Model):
    user = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="webauthn_credentials"
    )
    credential_id = models.CharField(max_length=255, unique=True, db_index=True)
    public_key = models.TextField()
    sign_count = models.PositiveIntegerField(default=0)
    transports = models.JSONField(default=list, blank=True)
    device_label = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.device_label or self.credential_id[:12]}"


class WebAuthnChallenge(models.Model):
    # A used-nonce ledger for single-use WebAuthn challenge enforcement - a row
    # is inserted only when a challenge is actually consumed by a successful
    # verify call (see accounts/views.py::_consume_challenge), not when it's
    # issued. The unique constraint on `jti` rejects a replayed request.
    jti = models.CharField(max_length=64, unique=True)
    consumed_at = models.DateTimeField(auto_now_add=True)
