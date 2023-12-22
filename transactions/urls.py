from django.urls import path

from transactions import views

urlpatterns = [
    path("", views.TransactionsLC.as_view(), name="LC-Transactions"),
    path("<uuid:pk>/",views.TransactionsRUD.as_view(),name='RUD-Transactions'),
    path("commodities/",views.CommodityLC.as_view(),name="LC-commodity"),
    path("commodities/<uuid:pk>/",views.CommodityRUD.as_view(),name="RUD-commodity"),
    path("sources/",views.SourcesLC.as_view(),name="LC-source"),
    path("sources/<uuid:pk>/",views.SourcesRUD.as_view(),name="RUD-source"),
    path("internalTransactions/",views.InternalTransactionsLC.as_view(),name="LC-source"),
    path("internalTransactions/<uuid:pk>/",views.InternalTransactionsRUD.as_view(),name="RUD-source"),
]
