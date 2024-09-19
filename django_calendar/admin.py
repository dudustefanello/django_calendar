from django.contrib import admin

from django_calendar.models import *

admin.site.register([
    Calendar,
    Event,
    ExDate,
    RecurrencyRule,
])
