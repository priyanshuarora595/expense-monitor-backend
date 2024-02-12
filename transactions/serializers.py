from rest_framework import serializers
from django.utils import timezone
from transactions.models import Transactions,Commodity,Sources,InternalTransactions


class TransactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transactions
        fields = [
            "id",
            "date",
            "user",
            "source",
            "transaction_type",
            "amount",
            "commodity",
            "comments",
        ]
        
        extra_kwargs = {'user': {'write_only': True}}
        
    def to_representation(self, obj):
        ret = super(TransactionsSerializer, self).to_representation(obj)
        ret["commodity"] = CommoditySerializer(Commodity.objects.get(id=ret["commodity"])).data
        ret["source"] = SourcesSerializer(Sources.objects.get(id=ret["source"])).data
        obj.date = timezone.localtime(obj.date)
        ret['date'] = obj.date.strftime('%Y-%m-%d %H:%M')
        return ret
    
    
class InternalTransactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalTransactions
        fields = [
            "id",
            "date",
            "user",
            "source",
            "destination",
            "amount",
            "comments",
        ]
        
        extra_kwargs = {'user': {'write_only': True}}
        
    def to_representation(self, obj):
        ret = super(InternalTransactionsSerializer, self).to_representation(obj)
        ret["source"] = SourcesSerializer(Sources.objects.get(id=ret["source"])).data
        ret["destination"] = SourcesSerializer(Sources.objects.get(id=ret["destination"])).data
        obj.date = timezone.localtime(obj.date)
        ret['date'] = obj.date.strftime('%Y-%m-%d %H:%M')
        return ret
    
class CommoditySerializer(serializers.ModelSerializer):
    class Meta:
        model = Commodity
        fields = [
            "id",
            'user',
            "name"
        ]
        extra_kwargs = {'user': {'write_only': True}}
        
    def to_representation(self, obj):
        ret = super(CommoditySerializer, self).to_representation(obj)
        # del ret['user']
        return ret
        
class SourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sources
        fields = [
            "id",
            'user',
            "name",
            'default'
        ]
        extra_kwargs = {'user': {'write_only': True}}
        
    def to_representation(self, obj):
        ret = super(SourcesSerializer, self).to_representation(obj)
        # del ret['user']
        return ret
    
    def save(self, **kwargs):
        request = self.context.get("request")
        request_data = request.data
        if request_data['default']=='true':
            user = request_data['user']
            sources = Sources.objects.filter(user=user)
            for source in sources:
                source.default=False
                source.save()
        return super().save(**kwargs)
