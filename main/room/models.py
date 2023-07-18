from django.db import models
from jdatetime import datetime
from home.models import Student, Plan
from django.utils import timezone
import locale
# Create your models here.

class Schedule(models.Model):
    week_days = [('شنبه','شنبه'),
                 ('یکشنبه','یکشنبه'),
                 ('دوشنبه','دوشنبه'),
                 ('سه شنبه','سه شنبه'),
                 ('چهار شنبه','چهار شنبه'),
                 ('پنج شنبه','پنج شنبه'),
                 ('جمعه','جمعه'),
                 ]

    day = models.CharField(max_length=48, choices=week_days)
    def get_now_time():
        return datetime.now().strftime('%Y/%m/%d')
    date = models.CharField(max_length=48, default=get_now_time)
    
    @property
    def items(self):
        return ScheduleItem.objects.filter(ScheduleRelated= self)
    def __str__(self):
        return self.day + self.date
        
class ScheduleItem(models.Model):
    grades = [
        ('دهم','دهم'),
        ('یازدهم','یازدهم'),
        ('دوازدهم','دوازدهم'),
    ]
    ScheduleRelated= models.ForeignKey(Schedule, on_delete=models.CASCADE)
    grade = models.CharField(max_length=50, choices=grades)
    time = models.CharField(max_length=100)
    toDo = models.CharField(max_length=256)


class room(models.Model):
    Room_title = models.CharField(max_length=16)
    plan = models.ManyToManyField(Plan)
    ScheduleRelated = models.ForeignKey(Schedule, on_delete=models.CASCADE, null=True)
    enable = models.BooleanField(default=False)
    def __str__(self):
        return 'MAIN ROOM'
