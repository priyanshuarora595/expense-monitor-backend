from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from transactions.models import Transactions,Commodity,Sources,InternalTransactions
from transactions.serializers import TransactionsSerializer,CommoditySerializer,SourcesSerializer,InternalTransactionsSerializer
from transactions.custom_permissions import IsOwner
from transactions.custom_pagination import CustomPagination

from django_filters.rest_framework import DjangoFilterBackend

class TransactionsLC(ListCreateAPIView):
    queryset=Transactions.objects.all().order_by("-date")
    serializer_class = TransactionsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends=[DjangoFilterBackend]
    filterset_fields = ['transaction_type','source','commodity']
    pagination_class = CustomPagination
    
    
    def get_queryset(self):
        if self.request.method == 'GET':
            # Return a specific queryset for GET requests
            date_param = self.request.query_params.get('date')

        # Filter transactions based on the provided date parameter
            if date_param:
                month=date_param.split('-')[1]
                year=date_param.split('-')[0]
                queryset = super().get_queryset().filter(user=self.request.user.id,date__month=month,date__year=year)
                return queryset
            return super().get_queryset().filter(user=self.request.user.id)
        else:
            # Return a different queryset for POST requests
            return super().get_queryset()
    
    
    def post(self, request, *args, **kwargs):
        request.data["user"] = request.user.id
        return super().post(request=request,*args,**kwargs)
    

class TransactionsRUD(RetrieveUpdateDestroyAPIView):
    queryset=Transactions.objects.all()
    serializer_class = TransactionsSerializer
    permission_classes = [IsAuthenticated,IsOwner]
    
    def patch(self, request, *args, **kwargs):
        request.data["user"] = request.user.id
        return super().patch(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        request.data["user"] = request.user.id
        return super().put(request, *args, **kwargs)

class CommodityLC(ListCreateAPIView):
    queryset=Commodity.objects.all().order_by("name")
    serializer_class = CommoditySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.method == 'GET':
            # Return a specific queryset for GET requests
            return super().get_queryset().filter(user=self.request.user.id)
            # return Commodity.objects.filter(user=self.request.user.id)
        else:
            # Return a different queryset for POST requests
            return super().get_queryset()
        
    def post(self, request, *args, **kwargs):
        request.data["user"] = request.user.id
        return super().post(request=request,*args,**kwargs)

class CommodityRUD(RetrieveUpdateDestroyAPIView):
    queryset=Commodity.objects.all()
    serializer_class = CommoditySerializer
    permission_classes = [IsAuthenticated,IsOwner]
    
    def patch(self, request, *args, **kwargs):
        request.data["user"] = request.user.id
        return super().patch(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        request.data["user"] = request.user.id
        return super().put(request, *args, **kwargs)
    
    
class SourcesLC(ListCreateAPIView):
    queryset=Sources.objects.all().order_by("id")
    serializer_class = SourcesSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.method == 'GET':
            return Sources.objects.filter(user=self.request.user.id)
        else:
            # Return a different queryset for POST requests
            return super().get_queryset()
        
    def post(self, request, *args, **kwargs):
        request.data["user"] = request.user.id
        return super().post(request=request,*args,**kwargs)


class SourcesRUD(RetrieveUpdateDestroyAPIView):
    queryset=Sources.objects.all()
    serializer_class = SourcesSerializer
    permission_classes = [IsAuthenticated,IsOwner]
    
    def patch(self, request, *args, **kwargs):
        request.data["user"] = request.user.id
        return super().patch(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        request.data["user"] = request.user.id
        return super().put(request, *args, **kwargs)


class InternalTransactionsLC(ListCreateAPIView):
    queryset=InternalTransactions.objects.all().order_by("-date")
    serializer_class = InternalTransactionsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends=[DjangoFilterBackend]
    filterset_fields = ['destination','source']
    pagination_class = CustomPagination
    
    def get_queryset(self):
        if self.request.method == 'GET':
            # Return a specific queryset for GET requests
            date_param = self.request.query_params.get('date')

        # Filter transactions based on the provided date parameter
            if date_param:
                month=date_param.split('-')[1]
                year=date_param.split('-')[0]
                queryset = super().get_queryset().filter(user=self.request.user.id,date__month=month,date__year=year)
                return queryset
            return super().get_queryset().filter(user=self.request.user.id)
        else:
            # Return a different queryset for POST requests
            return super().get_queryset()
    
    
    def post(self, request, *args, **kwargs):
        request.data["user"] = request.user.id
        return super().post(request=request,*args,**kwargs)
    

class InternalTransactionsRUD(RetrieveUpdateDestroyAPIView):
    queryset=InternalTransactions.objects.all()
    serializer_class = InternalTransactionsSerializer
    permission_classes = [IsAuthenticated,IsOwner]
    
    def patch(self, request, *args, **kwargs):
        request.data["user"] = request.user.id
        return super().patch(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        request.data["user"] = request.user.id
        return super().put(request, *args, **kwargs)