from django.contrib import admin
from .models import room, Schedule, ScheduleItem

# Register your models here.
admin.site.register(room)
admin.site.register(Schedule)
admin.site.register(ScheduleItem)