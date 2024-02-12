from rest_framework import serializers

from balance.models import Balance

from transactions.models import Sources
from transactions.serializers import SourcesSerializer


class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = [
            "id",
            "user",
            "year",
            "month",
            "source",
            "first_day_amount",
            "last_day_amount",
        ]
        
        extra_kwargs = {
        'user': {'write_only': True},
    }

    def to_representation(self, obj):
        ret = super(BalanceSerializer, self).to_representation(obj)
        ret["source"] = SourcesSerializer(Sources.objects.get(id=ret["source"])).data
        ret["month"] = str(ret["month"]).zfill(2)
        return ret
