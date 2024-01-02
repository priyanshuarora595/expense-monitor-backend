from django.contrib.auth import authenticate
from django.core.mail import send_mail

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView , RetrieveUpdateDestroyAPIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny , IsAdminUser
import uuid
import os
from django_filters.rest_framework import DjangoFilterBackend

from accounts.models import Account
from accounts.serializers import AccountSerializer
from accounts.custom_permissions import IsOwner

from ExpenseMonitor.settings import EMAIL_HOST_USER


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
        try:
            email = request.data.get("email")
            user = self.queryset.get(email=email)
            if user:
                user.forget_password_token = uuid.uuid4()
                user.save()
                send_mail(
                    subject="Password reset token",
                    message=f"""To reset your account password,click on the following link 
                    {os.getenv("FRONTEND_URL")+"reset_password.html?id="+str(user.forget_password_token)} """,
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
