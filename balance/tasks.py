from transactions.models import Transactions, Commodity, Sources, InternalTransactions
from balance.models import Balance
from datetime import datetime
from django.db.models import Sum


def calculate_expenditure(
    user_id=1, month=datetime.now().month, year=datetime.now().year
):
    sources = Sources.objects.filter(user=user_id).values_list("id", "name")
    internalTransactions = InternalTransactions.objects.filter(
        user=user_id, date__month=month, date__year=year
    )
    expenses = Transactions.objects.filter(
        user=user_id, date__month=month, date__year=year
    )
    credits = expenses.filter(transaction_type="credit")
    debits = expenses.filter(transaction_type="debit")
    balance = Balance.objects.filter(user=user_id, month=month, year=year).all()
    initial = 0
    remaining = 0
    internal_credits = 0
    internal_debits = 0
    data = {}
    
    for source in sources:
        source_initial = balance.filter(source__id=source[0]).aggregate(
            Sum("first_day_amount")
        )["first_day_amount__sum"]

        source_credits = credits.filter(source__id=source[0]).aggregate(Sum("amount"))[
            "amount__sum"
        ]
        internal_credits = internalTransactions.filter(
            destination__id=source[0]
        ).aggregate(Sum("amount"))["amount__sum"]

        source_debits = debits.filter(source__id=source[0]).aggregate(Sum("amount"))[
            "amount__sum"
        ]
        internal_debits = internalTransactions.filter(source__id=source[0]).aggregate(
            Sum("amount")
        )["amount__sum"]

        source_initial = source_initial if source_initial is not None else 0
        source_credits = source_credits if source_credits is not None else 0
        source_debits = source_debits if source_debits is not None else 0
        internal_credits = internal_credits if internal_credits is not None else 0
        internal_debits = internal_debits if internal_debits is not None else 0
        
        if any([source_initial,source_credits,source_debits,internal_credits,internal_debits]):
            data[source[1]] = {
                "initial": source_initial,
                "credits": source_credits,
                "internal_credits" : internal_credits,
                "debits": source_debits,
                "internal_transfer": internal_debits,
            }
            data[source[1]]["remaining"] = (
                data[source[1]]["initial"]
                + data[source[1]]["credits"]
                + data[source[1]]["internal_credits"]
                - data[source[1]]["debits"]
                - data[source[1]]['internal_transfer']
            )

            initial += data[source[1]]["initial"]
            remaining += data[source[1]]["remaining"]

    commodities = Commodity.objects.filter(user=user_id)
    detail_view = {}
    for commodity in commodities:
        commodity_credits = expenses.filter(
            commodity_id=commodity.id, transaction_type="credit"
        ).aggregate(Sum("amount"))["amount__sum"]

        commodity_debits = expenses.filter(
            commodity_id=commodity.id, transaction_type="debit"
        ).aggregate(Sum("amount"))["amount__sum"]

        detail_view[commodity.name] = {
            "credits": commodity_credits if commodity_credits is not None else 0,
            "debits": commodity_debits if commodity_debits is not None else 0,
        }

    total_credits = (
        credits.aggregate(Sum("amount"))["amount__sum"]
        if credits.aggregate(Sum("amount"))["amount__sum"] is not None
        else 0
    )
    total_debits = (
        debits.aggregate(Sum("amount"))["amount__sum"]
        if debits.aggregate(Sum("amount"))["amount__sum"] is not None
        else 0
    )

    return data, detail_view, total_credits, total_debits, initial, remaining
