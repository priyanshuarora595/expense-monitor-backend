from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.core import signing
from django.db import IntegrityError
from django.utils import timezone

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView , RetrieveUpdateDestroyAPIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
import uuid
import os
import base64
from dotenv import load_dotenv
from django_filters.rest_framework import DjangoFilterBackend

import webauthn
from webauthn.helpers import bytes_to_base64url, base64url_to_bytes
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    ResidentKeyRequirement,
    UserVerificationRequirement,
    PublicKeyCredentialDescriptor,
)

from accounts.models import Account, WebAuthnCredential, WebAuthnChallenge
from accounts.serializers import AccountSerializer
from accounts.custom_permissions import IsOwner

from ExpenseMonitor.settings import EMAIL_HOST_USER
# django.conf.settings (not a direct `from ExpenseMonitor.settings import ...`)
# so this actually respects whichever settings module DJANGO_SETTINGS_MODULE
# points at (e.g. a local/test override), instead of always reading the
# literal ExpenseMonitor/settings.py file regardless of environment.
from django.conf import settings as django_settings

load_dotenv()

class AccountCreateAPIView(CreateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    filter_backends = [DjangoFilterBackend]
    
    
class AccountRUDAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsOwner]
    



class LoginView(APIView):
    def post(self, request):
        if request.method == "POST":
            username = request.data.get("username")
            password = request.data.get("password")
            user = None
            try:
                user = Account.objects.get(username=username)
            except:
                return Response(
                    {"error": "User does not exist with this username"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            user = authenticate(username=username, password=password)

            if user:
                token, created = Token.objects.get_or_create(user=user)
                return Response(
                    {"token": token.key, "user_id": user.pk, "email": user.email},
                    status=status.HTTP_200_OK
                )

            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        request.auth.delete()  # Delete the user's authentication token
        return Response(
            {"success": "Successfully logged out"}, status=status.HTTP_200_OK
        )


class ChangePasswordView(APIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            current_password = request.data.get("current_password")
            new_password = request.data.get("new_password")
            user = authenticate(
                username=request.user.username, password=current_password
            )
            if user:
                user.set_password(new_password)
                user.save()
                return Response(
                    {"message": "password changed successfully"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "user does not exist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ForgotPasswordView(APIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def post(self, request):
        load_dotenv()
        try:
            email = request.data.get("email")
            user = self.queryset.get(email=email)
            if user:
                user.forget_password_token = uuid.uuid4()
                user.save()
                email_link = os.getenv("FRONTEND_URL")+"reset_password.html?id="+str(user.forget_password_token)
                send_mail(
                    subject="Password reset token",
                    message=f"""To reset your account password,click on the following link 
                    {email_link}""",
                    from_email=EMAIL_HOST_USER,
                    recipient_list=[user.email],
                )
                return Response(
                    {"message": "Email sent to reset password"},
                    status=status.HTTP_200_OK,
                )
        except Account.DoesNotExist as e:
            return Response(
                {"error": "user does not exist with this email"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def patch(self, request, token):
        try:
            user = self.queryset.get(forget_password_token=token)
            new_password = request.data.get("new_password")
            if user:
                user.set_password(new_password)
                user.forget_password_token = None
                user.save()
                return Response(
                    {"message": "password changed successfully"},
                    status=status.HTTP_200_OK,
                )
        except Account.DoesNotExist as e:
            return Response(
                {"error": "user does not exist with this token"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


def _consume_webauthn_challenge(challenge_b64):
    """Enforce single-use on a WebAuthn challenge. Returns True the first
    time a given challenge is consumed, False on any replay."""
    try:
        WebAuthnChallenge.objects.create(jti=challenge_b64)
        return True
    except IntegrityError:
        return False


class WebAuthnRegisterOptionsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        exclude_credentials = [
            PublicKeyCredentialDescriptor(id=base64url_to_bytes(cred.credential_id))
            for cred in user.webauthn_credentials.all()
        ]
        options = webauthn.generate_registration_options(
            rp_id=django_settings.WEBAUTHN_RP_ID,
            rp_name=django_settings.WEBAUTHN_RP_NAME,
            user_id=str(user.id).encode(),
            user_name=user.username,
            user_display_name=user.username,
            exclude_credentials=exclude_credentials,
            authenticator_selection=AuthenticatorSelectionCriteria(
                resident_key=ResidentKeyRequirement.PREFERRED,
                user_verification=UserVerificationRequirement.REQUIRED,
            ),
        )
        state = signing.dumps(
            {"challenge": bytes_to_base64url(options.challenge), "user_id": str(user.id)},
            salt="webauthn-register",
            key=django_settings.WEBAUTHN_SIGNING_KEY,
        )
        return Response(
            {"options": webauthn.options_to_json(options), "state": state},
            status=status.HTTP_200_OK,
        )


class WebAuthnRegisterVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        credential = request.data.get("credential")
        state = request.data.get("state")
        if not credential or not state:
            return Response(
                {"error": "Missing credential or state"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            payload = signing.loads(
                state, salt="webauthn-register", max_age=90, key=django_settings.WEBAUTHN_SIGNING_KEY
            )
        except signing.BadSignature:
            return Response(
                {"error": "This registration request has expired or is invalid, please try again"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if payload.get("user_id") != str(request.user.id):
            return Response(
                {"error": "This registration request does not belong to you"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not _consume_webauthn_challenge(payload["challenge"]):
            return Response(
                {"error": "This registration request was already used"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            verification = webauthn.verify_registration_response(
                credential=credential,
                expected_challenge=base64url_to_bytes(payload["challenge"]),
                expected_rp_id=django_settings.WEBAUTHN_RP_ID,
                expected_origin=django_settings.WEBAUTHN_ORIGIN,
                require_user_verification=True,
            )
        except Exception as e:
            return Response(
                {"error": f"Could not verify registration: {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        transports = []
        if isinstance(credential, dict):
            transports = credential.get("response", {}).get("transports", []) or []

        try:
            WebAuthnCredential.objects.create(
                user=request.user,
                credential_id=bytes_to_base64url(verification.credential_id),
                public_key=base64.b64encode(verification.credential_public_key).decode(),
                sign_count=verification.sign_count,
                transports=transports,
                device_label=request.META.get("HTTP_USER_AGENT", "")[:100],
            )
        except IntegrityError:
            return Response(
                {"error": "This device is already registered"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"success": True}, status=status.HTTP_200_OK)


class WebAuthnLoginOptionsView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        options = webauthn.generate_authentication_options(
            rp_id=django_settings.WEBAUTHN_RP_ID,
            user_verification=UserVerificationRequirement.REQUIRED,
        )
        state = signing.dumps(
            {"challenge": bytes_to_base64url(options.challenge)},
            salt="webauthn-login",
            key=django_settings.WEBAUTHN_SIGNING_KEY,
        )
        return Response(
            {"options": webauthn.options_to_json(options), "state": state},
            status=status.HTTP_200_OK,
        )


class WebAuthnLoginVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        credential = request.data.get("credential")
        state = request.data.get("state")
        if not credential or not state:
            return Response(
                {"error": "Missing credential or state"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            payload = signing.loads(
                state, salt="webauthn-login", max_age=90, key=django_settings.WEBAUTHN_SIGNING_KEY
            )
        except signing.BadSignature:
            return Response(
                {"error": "This login request has expired or is invalid, please try again"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not _consume_webauthn_challenge(payload["challenge"]):
            return Response(
                {"error": "This login request was already used"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        credential_id = credential.get("id") if isinstance(credential, dict) else None
        if not credential_id:
            return Response({"error": "Malformed credential"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            stored = WebAuthnCredential.objects.select_related("user").get(
                credential_id=credential_id
            )
        except WebAuthnCredential.DoesNotExist:
            return Response(
                {"error": "This device is not registered for fingerprint login"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            verification = webauthn.verify_authentication_response(
                credential=credential,
                expected_challenge=base64url_to_bytes(payload["challenge"]),
                expected_rp_id=django_settings.WEBAUTHN_RP_ID,
                expected_origin=django_settings.WEBAUTHN_ORIGIN,
                credential_public_key=base64.b64decode(stored.public_key),
                credential_current_sign_count=stored.sign_count,
                require_user_verification=True,
            )
        except Exception as e:
            return Response(
                {"error": f"Could not verify login: {e}"}, status=status.HTTP_401_UNAUTHORIZED
            )

        stored.sign_count = verification.new_sign_count
        stored.last_used_at = timezone.now()
        stored.save(update_fields=["sign_count", "last_used_at"])

        token, created = Token.objects.get_or_create(user=stored.user)
        return Response(
            {"token": token.key, "user_id": stored.user.pk, "email": stored.user.email},
            status=status.HTTP_200_OK,
        )


class WebAuthnCredentialDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, credential_id):
        deleted, _ = WebAuthnCredential.objects.filter(
            user=request.user, credential_id=credential_id
        ).delete()
        if deleted:
            return Response({"success": True}, status=status.HTTP_200_OK)
        return Response({"error": "Credential not found"}, status=status.HTTP_404_NOT_FOUND)
