from django.db import models
from ExpenseMonitor.settings import AUTH_USER_MODEL
import uuid

# Create your models here.


class Commodity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    class Meta:
        # Enforce a unique constraint on the combination of column1 and column2
        unique_together = ("user", "name")

    def __str__(self) -> str:
        return str(self.name)


class Sources(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    default = models.BooleanField(default=False)

    class Meta:
        # Enforce a unique constraint on the combination of column1 and column2
        unique_together = ("user", "name")


class Transactions(models.Model):
    class Transaction_type(models.TextChoices):
        CREDIT = "credit", "credit"
        DEBIT = "debit", "debit"
        TRANSFER = "transfer", "transfer"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name="date")
    source = models.ForeignKey(
        Sources,
        verbose_name="source",
        max_length=30,
        on_delete=models.SET_NULL,
        null=True,
    )
    transaction_type = models.CharField(
        verbose_name="transaction_type", choices=Transaction_type.choices, max_length=10
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    commodity = models.ForeignKey(
        Commodity, verbose_name="commodity", on_delete=models.SET_NULL, null=True
    )
    comments = models.TextField(verbose_name="comments")


class InternalTransactions(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name="date")
    source = models.ForeignKey(
        Sources,
        verbose_name="source",
        related_name="source",
        max_length=30,
        on_delete=models.SET_NULL,
        null=True,
    )
    destination = models.ForeignKey(
        Sources,
        verbose_name="destination",
        related_name="destination",
        max_length=30,
        on_delete=models.SET_NULL,
        null=True,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    comments = models.TextField(verbose_name="comments")