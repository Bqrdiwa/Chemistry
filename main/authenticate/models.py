from django.db import models
from django import forms
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.views import LoginView 
import re
from django.core.exceptions import ValidationError
from home.models import Student
import random
import requests

# Create your models here.

class RegisterForm(forms.ModelForm):
    phone_number = forms.CharField(max_length=10,widget=forms.TextInput(attrs={'class':"form-field", 'type':"tel" ,'placeholder':"+98 IR", 'id':"reg_phone"
                           ,'maxlength':"10" ,'onkeypress':'validate(event)'}))
    username = forms.CharField(max_length=16,widget=forms.TextInput(attrs={'class':"form-field" ,'type':"text", 'placeholder':"نام کاربری به انگلیسی", 'id':"reg_username"}))

    password1 = forms.CharField(max_length=16,widget=forms.PasswordInput(attrs={'class':"form-field" ,'type':"password" ,'placeholder':"رمز عبور", 'id':"reg_pass" 
                           ,'pattern':".{5,}"}))
    password2 = forms.CharField(max_length=16,widget=forms.PasswordInput(attrs={'class':"form-field" ,'type':"password" ,'placeholder':"تکرار رمز عبور", 'id':"reg_pass_confirm" 
                           ,'pattern':".{5,}"}))

    class Meta():
        model = Student
        fields = ['username','password','phone_number']

class LoginForm(forms.ModelForm):
    username = forms.CharField(max_length=16,widget=forms.TextInput(attrs={'class':"form-field", 'type':"text" ,'placeholder':"اینجا وارد کنید" ,'id':"login_username"}))
    password = forms.CharField(max_length=16,widget=forms.PasswordInput(attrs={'class':"form-field", 'type':"password" ,'placeholder':"اینجا وارد کنید" ,'id':"login_pass"}))    
    
    class Meta():
        model = Student
        fields = ['username','password']
        
class ProfileForm(forms.ModelForm):
    c_subject = [('',''),('تجربی','تجربی'),('ریاضی','ریاضی'),('انسانی','انسانی')]
    subject = forms.ChoiceField(choices=c_subject,required=False, widget=forms.Select(attrs={'class':"select-wrapper"}))
    
    c_grade = [('',''),('دهم','دهم'),('یازدهم','یازدهم'),('دوازدهم','دوازدهم'),('فارغ التحصیل','فارغ التحصیل'),('دانشگاه','دانشگاه')]
    grade = forms.ChoiceField(choices=c_grade,required=False,widget=forms.Select(attrs={'class':"select-wrapper"}))
    
    username = forms.CharField(max_length=36,widget=forms.TextInput(attrs={'class':"form-field",'style':"text-align: left;",'id':'username_input'}),required=False)
    full_name = forms.CharField(max_length=36,widget=forms.TextInput(attrs={'class':"form-field",'id':'fullname_input'}),required=False)
    
    class Meta():
        model = Student
        fields = ['subject','grade','username','full_name']

class VertificationCode(models.Model):
    studentRelated = models.OneToOneField(Student, on_delete=models.CASCADE)
    code = models.IntegerField(default=0)
    sTime = models.IntegerField(default=0)

    def codeGEN(self, stime):
        number = random.randint(1001,9999)
        self.code = number 
        self.sTime = stime
        self.save()

        self.studentRelated.send_vertification_code(self.code)
        return number
        
class VertificationCodePhone(models.Model):
    phone_number = models.CharField(max_length=10)
    sTime = models.IntegerField(default=0)
    code = models.IntegerField(default=0)
    
    def codeGEN(self, stime, username):
        number = random.randint(1001,9999)
        self.code = number 
        self.sTime = stime
        sender = '+983000505'
        pattern_code = '6a0j2m5jura5rtg'
        api_key = 'inj29QmiusdNG2Meu0kbD2LHG9n18Fi1i5nUGkEYkWo='
        to = '0'+self.phone_number
        url = f'http://ippanel.com:8080/?apikey={api_key}&pid={pattern_code}&fnum={sender}&tnum={to}&p1=username&p2=verificationCode&v1={username}&v2={number}'
        req = requests.get(url)
        self.save()
        return [req.status_code, req.content]

