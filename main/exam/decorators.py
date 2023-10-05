from exam.models import Result, Exam
from django.shortcuts import redirect
from django.contrib import messages
from datetime import datetime, timedelta
from django.utils import timezone
import pytz

def result_permission(view_func):
    def wrapper(request,pk ,*args, **kwargs):
        admi = False
        if request.user.groups.filter(name='Admin').count() > 0:
            admi = True
        try:
            result = Result.objects.get(pk = pk)
        except:
            messages.success(request, f'کارنامه ای با ایدی {pk}# پیدا نشد')
            return redirect('exam')
        
        exam = result.Exam_related  
        ttz = pytz.timezone('Asia/Tehran')
        examendTime = (datetime.combine(exam.sdate, exam.stime) + timedelta(minutes=exam.time)).astimezone(ttz)
        ddf = (examendTime - timezone.now().astimezone(ttz)).total_seconds()
        
        if ddf < 0:
            if result.timeSpend == None:
                result.timeSpend = timedelta(minutes=exam.time)
                result.save()
            return view_func(request,pk ,*args,**kwargs)
        elif ddf > exam.time * 60:
            messages.success(request, f'آزمون شروع نشده کارنامه چی رو میخوای ؟ :/')
            return redirect('exam')
        else:
            messages.success(request, f'برای مشاهده کارنامه آزمون {exam.name} تا پایان آزمون صبر نمایید')
            return redirect('exam')
    return wrapper


def exam_permission(view_func):
    def wrapper(request,name,*args,**kwargs):
        # if the users already test himself in the exam!
        try:
            exam = Exam.objects.get(name = name)
        except:
            messages.success(request, f'آزمونی با نام {name} پیدا نشد')
            return redirect('exam')
        
        plans_are_good = exam.plans.all()
        users_plans = request.user.plans.all()
        ac = False
        for i in plans_are_good:
            if i in users_plans:
                ac = True
        if plans_are_good.count() == 0:ac =True
        if not ac:
            messages.success(request, f'شما برای شرکت در آزمون {exam.name} باید حداقل یکی از دوره های این آزمون را خریداری کنید.')
            return redirect('exam')
        
        #timeCheck
        tehranTimeZone = pytz.timezone('Asia/Tehran')
        endTime = (datetime.combine(exam.sdate, exam.stime) + timedelta(minutes=exam.time)).astimezone(tehranTimeZone)
        nowTime = timezone.now().astimezone(tehranTimeZone)
        td = (endTime-nowTime).total_seconds()
        if td > exam.time*60:
            messages.success(request, f'آزمون {exam.name} هنوز شروع نشده. زمان شروع آزمون : {exam.stime}')
            return redirect('exam')
        
        if td < 0:
            try:
                result = exam.result_set.get(participant= request.user)
                return redirect('exam-result',result.pk)
            except:pass
            messages.success(request, f'زمان شرکت در آزمون {exam.name} به پایان رسیده.')
            return redirect('exam')
        


        return view_func(request, name, *args, **kwargs)
        #if the user have the role to participant
        
       

        
            
    return wrapper
        