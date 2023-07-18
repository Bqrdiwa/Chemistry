from exam.models import Result, Exam
from django.shortcuts import redirect
from django.contrib import messages

def result_permission(view_func):
    def wrapper(request,pk ,*args, **kwargs):
        admi = False
        if request.user.groups.filter(name='Admin').count() > 0:
            admi = True
        try:
            result = Result.objects.get(pk = pk)
            if result.Exam_related.status != 'Ended' and (not admi):
                messages.success(request, f'برای مشاهده کارنامه آزمون {result.Exam_related.name} تا پایان آزمون صبر نمایید')
                return redirect('exam')
        except:
            messages.success(request, f'کارنامه ای با ایدی {pk}# پیدا نشد')
            return redirect('exam')
        
        return view_func(request,pk ,*args,**kwargs)
    return wrapper


def exam_permission(view_func):
    def wrapper(request,name,*args,**kwargs):
        # if the users already test himself in the exam!
        try:
            exam = Exam.objects.get(name = name)
        except:
            messages.success(request, f'آزمونی با نام {name} پیدا نشد')
            return redirect('exam')
        try:
            result = exam.result_set.get(participant= request.user)
            return redirect('exam-result',result.pk)
        except:pass
        
        admi_perm = False
        if request.user.groups.filter(name='Admin').count()>0:
            admi_perm=True
        
        if admi_perm or exam.status == 'Started':
             return view_func(request,name,*args,**kwargs)
        else:
            if exam.status == 'None':
                messages.success(request, f'آزمون {exam.name} هنوز شروع نشده زمان شروع آزمون: {exam.startTime}')
                return redirect('exam')
            else:
                messages.success(request, f'زمان شما برای شرکت در این آزمون به اتمام رسیده')
                return redirect('exam')
        #if the user have the role to participant
        
       

        
            
    return wrapper
        