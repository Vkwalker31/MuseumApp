"""Контекстный процессор: таймзона, даты в локальной зоне и UTC, текстовый календарь."""
from calendar import TextCalendar
from datetime import timezone as dt_timezone

from django.conf import settings
from django.utils import timezone


def datetime_info(request):
    now_local = timezone.localtime()
    now_utc = now_local.astimezone(dt_timezone.utc)
    cal = TextCalendar(firstweekday=0)
    text_calendar = cal.formatmonth(now_local.year, now_local.month)
    from .cart import cart_count
    return {
        'user_timezone': settings.TIME_ZONE,
        'now_local_str': now_local.strftime('%d/%m/%Y'),
        'now_utc_str': now_utc.strftime('%d/%m/%Y'),
        'text_calendar': text_calendar,
        'cart_count': cart_count(request.session),
    }
