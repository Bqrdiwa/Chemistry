from exam.models import virtualExam
from django.shortcuts import redirect
from django.contrib import messages

def virtualExamNotEnded(view_func):
    def wrapper(request, pk, *args, **kwargs):
        virtualExamRelated = virtualExam.objects.get(pk = pk)
        if virtualExamRelated.status != 'ended':
            return view_func(request,pk ,*args,**kwargs)
        else:
            messages.success(request, f'آزمون ازمایشی مورد نظر شما با ایدی <span style="font-family:monospace">{pk}#</span> پایان یافته')
            return redirect('question-bank')
    return wrapper