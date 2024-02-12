from rest_framework.generics import  ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend

from balance.models import Balance
from balance.serializers import BalanceSerializer
from balance.custom_permissions import IsOwner
from balance.custom_pagination import CustomPagination
from balance.tasks import calculate_expenditure

from api.views import ExportView

from datetime import datetime as dt

class BalanceLC(ListCreateAPIView):
    queryset=Balance.objects.all().order_by("-year",'-month')
    serializer_class=BalanceSerializer
    permission_classes=[IsAuthenticated]
    filter_backends=[DjangoFilterBackend]
    filterset_fields = ['source','year','month']
    # pagination_class = CustomPagination
    # pagination_class = CustomPagination
    
    def get_pagination_class(self):
        # Check if a specific query parameter is present in the request
        if self.request.query_params.get('disable_pagination'):
            return None  # Disable pagination
        return CustomPagination  # Enable pagination
    
    def get_queryset(self):
        if self.request.method=="GET":
            return super().get_queryset().filter(user=self.request.user.id)
        return super().get_queryset()
    
    def post(self, request, *args, **kwargs):
        request.data["user"] = request.user.id
        return super().post(request=request,*args,**kwargs)
    
    def get(self, request, *args, **kwargs):
        if request.query_params.get("export")=='true':
            return ExportView().process_data(super().get(request,*args,**kwargs).data)
        return  super().get(request,*args,**kwargs)
            


class BalanceRUD(RetrieveUpdateDestroyAPIView):
    queryset=Balance.objects.all()
    serializer_class=BalanceSerializer
    permission_classes=[IsAuthenticated,IsOwner]
    
class BalanceDetailData(APIView):
    queryset=Balance.objects.all()
    serializer_class=BalanceSerializer
    permission_classes=[IsAuthenticated,IsOwner]
    
    
    def get(self,request,pk):
        balance = Balance.objects.get(id=pk)
        month = balance.month
        year= balance.year
        data, detail_view, total_credits, total_debits,initial,remaining =calculate_expenditure(user_id=request.user.id,month=month,year=year)
        month = dt(year=1, month=balance.month, day=1).strftime('%B')
        context_data = {'month':month,'year':balance.year,'data':data,'detail_view':detail_view,'total_credits':total_credits,'total_debits':total_debits,'initial':initial,'remaining':remaining}
        
        return Response(
                    context_data,
                    status=status.HTTP_200_OK,
                )