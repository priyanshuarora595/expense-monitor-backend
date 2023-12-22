from django.urls import path

from accounts import views

urlpatterns = [
    path("", views.AccountCreateAPIView.as_view(), name="create-account"),
    path(
        "change-password/", views.ChangePasswordView.as_view(), name="change_password"
    ),
    path(
        "forgot-password/", views.ForgotPasswordView.as_view(), name="forgot_password"
    ),
    path(
        "forgot-password/<uuid:token>",
        views.ForgotPasswordView.as_view(),
        name="reset_password",
    ),
]
