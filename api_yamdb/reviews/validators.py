from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(value):
    """Проверяет, что год произведения не больше текущего."""
    now = timezone.now().year
    if value > now:
        raise ValidationError(f'{value} не больше {now}')
