from django.urls import path, include
from accounts import views as accountviews
from api import views as apiviews



urlpatterns = [
    path("accounts/", include("accounts.urls")),
    path("login/", accountviews.LoginView.as_view(), name="user_login"),
    path("logout/", accountviews.LogoutView.as_view(), name="user_logout"),
    path("webauthn/register/options/", accountviews.WebAuthnRegisterOptionsView.as_view(), name="webauthn_register_options"),
    path("webauthn/register/verify/", accountviews.WebAuthnRegisterVerifyView.as_view(), name="webauthn_register_verify"),
    path("webauthn/login/options/", accountviews.WebAuthnLoginOptionsView.as_view(), name="webauthn_login_options"),
    path("webauthn/login/verify/", accountviews.WebAuthnLoginVerifyView.as_view(), name="webauthn_login_verify"),
    path("webauthn/credentials/<str:credential_id>/", accountviews.WebAuthnCredentialDeleteView.as_view(), name="webauthn_credential_delete"),
    path("expenses/",include("transactions.urls")),
    path("balances/",include("balance.urls")),
    path("export/",apiviews.ExportView.as_view(),name= "export_data")
]
