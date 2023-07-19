from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import  login , logout , authenticate
from .models import LoginForm,RegisterForm,ProfileForm, VertificationCode, VertificationCodePhone
from django.contrib.auth.models import Group
import re
from django.http import JsonResponse
from exam.models import Exam, Result, ExamAir
from json import dumps
from home.models import Student


# Create your views here.


def Login(request):
    error_list = {}
    if request.user.is_authenticated:
        return redirect('profile')
    if request.method == 'POST':
        login_form  = LoginForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username,password=password)
        if user is not None:
            login(request=request,user=user)
            print('logged-in')
            messages.add_message(request, messages.SUCCESS, 'احراز هویت شما با موفقیت انجام شد')
            try:
                nextURL = request.GET['next']
                return redirect(nextURL)
            except:
                return redirect('profile')
        error_list = {'user+pass':'اطلاعات وارد شده غلط میباشند'}
    

    login_form = LoginForm()
    return render(request,'authenticate/login.html',context = {'title':'Login','lform':login_form,'errors':error_list})

def Register(request):
    error_list = {}
    if not request.user.is_authenticated:
        if request.method == 'POST':
            context = {}
            action = request.POST['action']
            if action == 'create_account':
                def clean(username,pass1,pass2,phone_number):
                    error_list = {}   
                    # username_vertification
                    
                        # already exist
                    try:
                        user = Student.objects.get(username=username)
                        error_list['reg_username'] =  'نام کاربری وارد شده قبلا استفاده شده'
                    except:
                        pass
                    
                        # wrong letters
                    mojaz = 'QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890_ '
                    persian_alefba = 'ضصثقفغعهخحجشسیبلاتنمظطزرذدئکوگجچپگگو'
                    counter = ''
                    for i in username:
                        if i not in mojaz:
                            if i not in counter:
                                counter += f' {i}'
                        if i in persian_alefba:
                            error_list['reg_username'] = 'لطفا نام کاربری را به انگلیسی وارد کنید'
                            counter = ''
                            break
                    if counter != '':
                        error_list['reg_username'] = f'{counter} :حروف غیر مجاز'
                    
                    # password equallity
                    if len(pass1)< 5:
                        error_list['reg_pass'] = 'پسورد شما باید بیشتر از 5 کاراکتر باشد'
                    if pass1 != pass2:
                        error_list['reg_pass_confirm'] = 'پسورد ها با یکدیگر مطابقت ندارند'
                    
                    # phone_number vertification
                        #wrong numbers
                    if re.search(r'(0|\+98)?([ ]|-|[()]){0,2}9[1|2|3|4|5|6|7|8|9]([ ]|-|[()]){0,2}(?:[0-9]([ ]|-|[()]){0,2}){8}',phone_number) == None:
                        error_list['reg_phone'] = 'شماره موبایل باید با عدد 9 شروع شود'

                        # already exist
                    try:
                        user = Student.objects.get(phone_number=phone_number)
                        error_list['reg_phone'] =  'کاربر دیگری با این شماره وجود دارد'
                    except:
                        pass
                        
                    return error_list
                username = request.POST['username']
                password1 = request.POST['password1']
                password2 = request.POST['password2']
                pn = request.POST['phone_number']
                error_list = clean(username,password1,password2,pn)
                if not error_list:
                    context['ERR'] = dumps({'HAS':'N'})
                    vc, created = VertificationCodePhone.objects.get_or_create(phone_number = pn)
                    sTime = int(request.POST['sTime'])
                    codeGenned = 'False'
                    if created:
                        vc.codeGEN(sTime, username)
                        codeGenned = 'True'
                    else:
                        timeDiff =  (sTime - vc.sTime )/1000
                        if timeDiff > 120:
                            vc.codeGEN(sTime, username)
                            codeGenned = 'True'
                        else:
                            context['ERRT'] = str(timeDiff)
                    context['codeGenned'] = codeGenned

                else:
                    error_list['HAS']='Y'
                    context['ERR'] = dumps(error_list)
            elif action == 'vc_verify':
                pn = request.POST['phone_number']
                vc = VertificationCodePhone.objects.get(phone_number = pn)
                context['ERR'] = 'None'
                if str(vc.code) == str(request.POST['code']):
                    user = Student.objects.create_user(username = request.POST['username'],password=request.POST['password'],phone_number= pn)
                    group = Group.objects.get(name='Member')
                    user.groups.add(group)
                    login(request,user)
                    messages.add_message(request, messages.SUCCESS, 'اکانت شما با موفقیت ساخته شد')
                else:
                    context['ERR'] = 'code'
                    
            return JsonResponse(context)
        else:
            register_form = RegisterForm()
            return render(request,'authenticate/register.html',context = {'title':'Register','rform':register_form,'errors':error_list})
    else:
        return redirect('profile')

@login_required
def Logout(request):
    if request.user.is_authenticated:
        logout(request=request)
        messages.success(request,'شما از اکانت خود با موفقیت خارج شدید')
        return redirect('home')

def ForgotPassword(request):
    if request.method == 'POST':
        context = {}
        action = request.POST['action']
        context['ERR'] = 'None'
        phone_number = request.POST['phone_number']
        if action == 'vc_send':
            try:
                student_related = Student.objects.get(phone_number = phone_number)
                vc, created = VertificationCode.objects.get_or_create(studentRelated = student_related)
                sTime = request.POST['sTime']
                codeGenned = 'False'
                if created:
                    vc.codeGEN(sTime)
                    codeGenned = 'True'
                else:
                    timeDiff =  (int(sTime) - vc.sTime )/1000
                    if timeDiff > 120:
                        vc.codeGEN(sTime)
                        codeGenned = 'True'
                    else:
                        context['ERRT'] = str(timeDiff)
                context['codeGenned'] = codeGenned
            except:
                context['ERR'] = 'phone_number'
        elif action == 'vc_verify':
            try:
                student_related = Student.objects.get(phone_number = phone_number)
                vc = VertificationCode.objects.get(studentRelated = student_related)
                code = request.POST['vertification_code']
                if str(vc.code) != str(code):
                    context['ERR'] = 'code'
            except:
                context['ERR'] = '404'
        elif action == 'change_pass':
            try:
                student_related = Student.objects.get(phone_number = phone_number)
                vc = VertificationCode.objects.get(studentRelated = student_related)
                code = request.POST['vertification_code']
                passcode = request.POST['password']
                if str(vc.code) != str(code):
                    context['ERR'] = '404'
                else:
                    student_related.set_password(passcode)
                    student_related.save()
            except:
                context['ERR'] = '404'
        return JsonResponse(context)
    else:
        
        return render(request, 'authenticate/forgotpassword.html')
    
@login_required  
def Profile(request):
    error_list = {}
    change_things = {}
    if request.method == 'POST':
        def clean(dtc):
            if dtc['username'] != '' and request.user.username != dtc['username']:
                pasport = 2
                # username_vertification
                
                    # already exist
                try:
                    user = Student.objects.get(username=dtc['username'])
                    error_list['username'] =  'نام کاربری وارد شده قبلا استفاده شده'
                except:
                    pasport -= 1
                
                    # wrong letters
                mojaz = 'QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890_ '
                persian_alefba = 'ضصثقفغعهخحجشسیبلاتنمظطزرذدئکوگجچپگگو'
                counter = ''
                for i in dtc['username']:
                    if i not in mojaz:
                        if i not in counter:
                            counter += f' {i}'
                    if i in persian_alefba:
                        error_list['username_Farsi'] = 'لطفا نام کاربری را به انگلیسی وارد کنید'
                        counter = ''
                        break
                if counter != '':
                    error_list['username'] = f'{counter} :حروف غیر مجاز'
                else:
                    pasport -=1
                    
                if pasport == 0:
                    change_things['username'] = dtc['username']
                    
            
            if dtc['full_name']:
                persian_alefba = ' ضصثقفغعهخحجشسیبلاتنمظطزرذدئکوگجچپگگو' 
                counter = ''
                for char in  dtc['full_name']:
                    if char not in persian_alefba:
                        counter += char+' '
                if counter != '':
                    error_list['full_name'] = f'{counter}:حروف غیر مجاز'
                else:
                    change_things['full_name'] = dtc['full_name']

            return error_list

        form = ProfileForm(request.POST)
        data = clean(request.POST)
        if not data:
            user = Student.objects.get(username = request.user.username)
            for i in change_things.keys():
                if i =='username':
                    user.username = change_things['username']
                if i == 'full_name':
                    user.full_name = change_things['full_name']
            user.subject = request.POST['subject']
            user.grade = request.POST['grade']
            user.save()
            messages.success(request,'اطلاعات شما با موفقیت تغییر پیدا کرد')
            return redirect('home')
    
    else:
        form = ProfileForm()
        
    exams = {'ended':[],'not_ended':[],'not_started':[]}
    all_exams = Exam.objects.all()
    finded = False
    for exam in all_exams:
        try:
            result = Result.objects.get(Exam_related = exam, participant = request.user)
            exams['ended'].append(result)
            finded = True
        except:
            try:
                ExamAir.objects.get(Exam_related = exam, student_related = request.user)
                exams['not_ended'].append(exam)
                finded = True
            except:
                if exam.status != 'Ended':
                    exams['not_started'].append(exam)
                    finded = True
    return render(request,'home/profile.html',context={'finded':finded, 'title':'Profile','form':form,'error_list':error_list,'HT':'پروفایل','exams':exams})
