from django.urls import path

from balance import views

urlpatterns = [
    path("", views.BalanceLC.as_view(), name="LC-balance"),
    path("<uuid:pk>/",views.BalanceRUD.as_view(),name='RUD-balance'),
    path("details/<uuid:pk>/",views.BalanceDetailData.as_view(),name='balance-detail'),
    path("details-range/",views.BalanceDetailRange.as_view(),name='balance-detail-range'),
]
