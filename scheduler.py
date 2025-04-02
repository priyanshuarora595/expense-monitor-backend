from dotenv import load_dotenv

load_dotenv()
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ExpenseMonitor.settings")
django.setup("DJANGO_SETTINGS_MODULE")

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from ExpenseMonitor.settings import EMAIL_HOST_USER
from accounts.models import Account
from balance.tasks import calculate_expenditure
from datetime import datetime as dt, timedelta


def prep_data_and_send_mail(user_id, month, year, user_email_id):
    data, detail_view, total_credits, total_debits, initial, remaining = (
        calculate_expenditure(user_id, month, year,monthly_auto=True)
    )
    month = dt(year=1, month=month, day=1).strftime("%B")
    context_data = {
        "month": month,
        "year": year,
        "data": data,
        "detail_view": detail_view,
        "total_credits": total_credits,
        "total_debits": total_debits,
        "initial": initial,
        "remaining": remaining,
    }
    html_message = render_to_string("balance.html", context_data)
    subject = f"Monthly Expenditure report for {month} {year}"
    message = f"""
    Hello
    Please find Monthly expenditure report for {month} {year}

    """

    email = EmailMultiAlternatives(
        subject,
        message,
        EMAIL_HOST_USER,
        [user_email_id],  # Sender's email address
    )
    email.attach_alternative(html_message, "text/html")
    email.send()


def is_first_day_of_month():
    today = dt.today()
    return today.day == 1


def go_one_day_back(date=None):
    if date is None:
        date = dt.today()
    previous_day = date - timedelta(days=1)
    return previous_day


def send_mail_last_day(month, year, user_id=None):
    if user_id:
        account = Account.objects.get(id=user_id)
        user_email_id = account.email
        prep_data_and_send_mail(user_id, month, year, user_email_id)
    else:
        accounts = Account.objects.all().values_list(
            "id", "email", "send_monthly_report"
        )
        for account in accounts:
            user_id = account[0]
            user_email_id = account[1]
            send_monthly_report = account[2]
            if send_monthly_report:
                prep_data_and_send_mail(user_id, month, year, user_email_id)


def my_daily_task():
    # Your job code here
    if is_first_day_of_month():
        previous_day = go_one_day_back()
        send_mail_last_day(previous_day.month, previous_day.year)
