from django.contrib import admin
from .models import Exam, Question, Result, ExamAir, Question_Solution
# Register your models here.

admin.site.register(Exam)
admin.site.register(Question)
admin.site.register(Result)
admin.site.register(ExamAir)
admin.site.register(Question_Solution)
