from django.contrib import admin
from .models import Student, Solution, Answer, SolutionLike, Feature, Plan
from exam.models import virtualExam

# Register your models here.
admin.site.register(Student)
admin.site.register(Solution)
admin.site.register(SolutionLike)
admin.site.register(Answer)
admin.site.register(virtualExam)
admin.site.register(Feature)
admin.site.register(Plan)
