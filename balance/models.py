from django.db import models
from transactions.models import Sources
from datetime import datetime
import uuid

from ExpenseMonitor.settings import AUTH_USER_MODEL
from balance.custom_validators import validate_month,validate_year

# Create your models here.
class Balance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    year = models.IntegerField(validators=[validate_year])
    month = models.IntegerField(validators=[validate_month])
    source = models.ForeignKey(Sources, on_delete=models.SET_NULL,null=True,
        verbose_name="source"
    )
    first_day_amount = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    last_day_amount = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    
    class Meta:
        # Enforce a unique constraint on the combination of column1 and column2
        unique_together = ('user', 'year','month','source')