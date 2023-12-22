from django.core.exceptions import ValidationError
from datetime import datetime



def validate_month(value):
    if 12<=int(value)<=1:
        raise ValidationError("month must be in range from 1 to 12 only.")

def validate_year(value):
    if datetime.now().year<=int(value)<=2000:
        raise ValidationError("year must be less than or equal to current year and greater than 2000")