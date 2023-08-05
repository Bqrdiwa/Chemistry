from exam.models import virtualExam
from django.shortcuts import redirect
from django.contrib import messages
from .models import Plan

def virtualExamNotEnded(view_func):
    def wrapper(request, pk, *args, **kwargs):
        virtualExamRelated = virtualExam.objects.get(pk = pk)
        if virtualExamRelated.status != 'ended':
            return view_func(request,pk ,*args,**kwargs)
        else:
            messages.success(request, f'آزمون ازمایشی مورد نظر شما با ایدی <span style="font-family:monospace">{pk}#</span> پایان یافته')
            return redirect('question-bank')
    return wrapper

def BasePlanReq(view_func):
    def wrapper(request, *args, **kwargs):
        user = request.user
        BasePlan = Plan.objects.get(pk=1)
        if BasePlan in user.plans.all():
            return view_func(request,*args,**kwargs)
        else:
            messages.success(request, f'شما برای دیدن این صفحه باید دوره {BasePlan.name} را داشته باشید')
            return redirect('plans')
    return wrapper