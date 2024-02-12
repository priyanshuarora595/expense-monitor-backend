from django.urls import path, include
from accounts import views as accountviews
from api import views as apiviews



urlpatterns = [
    path("accounts/", include("accounts.urls")),
    path("login/", accountviews.LoginView.as_view(), name="user_login"),
    path("logout/", accountviews.LogoutView.as_view(), name="user_logout"),
    path("expenses/",include("transactions.urls")),
    path("balances/",include("balance.urls")),
    path("export/",apiviews.ExportView.as_view(),name= "export_data")
]
