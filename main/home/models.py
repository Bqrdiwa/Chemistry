from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,Group
from .managers import CustomUserManager
from django.utils import timezone
from django import forms
from django.utils import timezone
import os
import requests

# Create your models here.
class Feature(models.Model):
    name = models.CharField(max_length=48)
    icon = models.CharField(max_length=12000, blank=True)
    
    def __str__(self):
        return self.name

class Plan(models.Model):
    name = models.CharField(max_length=48)
    features = models.ManyToManyField(Feature)
    price = models.CharField(max_length=120, default='0')
    def __str__(self):
        return self.name
    
    
class Student(PermissionsMixin,AbstractBaseUser):
    grad = [('',''),('دهم','دهم'),('یازدهم','یازدهم'),('دوازدهم','دوازدهم'),('فارغ التحصیل','فارغ التحصیل')]
    subjec = [('',''),('تجربی','تجربی'),('ریاضی','ریاضی'),('انسانی','انسانی')]
    username = models.CharField(max_length=32,unique=True)
    full_name = models.CharField(max_length=32,default='', blank=True)
    grade = models.CharField(max_length=16,choices=grad,default='', blank=True)
    subject = models.CharField(max_length=16,choices=subjec,default='')
    phone_number = models.CharField(max_length=10,default='', blank=True)
    date_created  = models.DateTimeField(default=timezone.now)
    plans = models.ManyToManyField(Plan, blank=True)
    
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    
    REQUIRED_FIELDS = ('phone_number',)
    objects = CustomUserManager()
    
    @property
    def get_name(self):
        if self.full_name != '':
            return self.full_name
        else:
            return self.username
        
    @property
    def value(self):
        results  = self.result_set.all().count()
        roles = self.groups.all().count()
        plans = self.plans.all().count()

        val = ((plans * 5 - 4) + (roles * 2 - 1) + results)/10
        if val > 10 :val = 10
        if val < 0:val = .5
        return val

    def send_sms(self, sms):
        sender = '+983000505'
        to = '0'+self.phone_number
        msg = sms
        uname = '09397962707'
        passw = 'Faraz@3242523601'

        url = f'https://ippanel.com/class/sms/webservice/send_url.php?from={sender}&to={to}&msg={sms} &uname={uname}&pass={passw}'
        req = requests.get(url)
        return [req.status_code, req.content]
        
    def send_vertification_code(self, vc):
        sender = '+983000505'
        pattern_code = '6a0j2m5jura5rtg'
        api_key = 'inj29QmiusdNG2Meu0kbD2LHG9n18Fi1i5nUGkEYkWo='
        to = '0'+self.phone_number
        url = f'http://ippanel.com:8080/?apikey={api_key}&pid={pattern_code}&fnum={sender}&tnum={to}&p1=username&p2=verificationCode&v1={self.username}&v2={vc}'
        req = requests.get(url)
        return [req.status_code, req.content]

    def __str__(self):
        return self.username

class Solution(models.Model):
    grad = [('دهم','دهم'),('یازدهم','یازدهم'),('دوازدهم','دوازدهم')]
    fasl = [('اول','فصل اول'),('دوم','فصل دوم'),('سوم','فصل سوم'),('چهارم','فصل چهارم')]
    title = models.CharField(max_length=128)
    content = models.CharField(max_length=480)
    moredata = models.ImageField(upload_to='probloms_pics', blank=True, null=True)
    sender = models.ForeignKey(Student, on_delete=models.CASCADE)
    position = models.CharField(default='باز', max_length=10)
    create_time = models.DateTimeField(default=timezone.now)
    publish = models.BooleanField(default=False)
    grade = models.CharField(max_length=16,choices=grad,default='')
    unit = models.CharField(max_length=16,choices=fasl,default='')
    def __str__(self):
        return f'Ticket By {self.sender.username} With Title Of {self.title}'

class Answer(models.Model):
    problom = models.OneToOneField(Solution, on_delete=models.CASCADE)
    content = models.CharField(max_length=480)
    subject = models.CharField(max_length=48,null=True)
    file = models.FileField(upload_to='probloms_files', blank=True, null=True)
    time = models.DateTimeField(default = timezone.now)
    
    @property
    def get_file_type(self):
        # Get the file extension
        extension = os.path.splitext(self.file.name)[1][1:]

        # Check if the extension indicates an image or video
        if extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
            return 'image'
        elif extension in ['mp4', 'avi', 'mkv', 'mov', 'wmv']:
            return 'video'
        else:
            return 'unknown'
    def __str__(self):
        return self.problom.sender.username + "'s" + ' Awnser'

class SolutionLike(models.Model):
    s = models.ForeignKey(Solution, on_delete=models.CASCADE)
    lover = models.ForeignKey(Student, on_delete=models.CASCADE)

    def __str__(self):
        return f'self.lover.username Liked #{self.s.pk} '
class solutionForm(forms.Form):
    title = forms.CharField(max_length=128)
    content = forms.CharField(max_length=480)
    moredata = forms.ImageField()

    
    class Meta:
        model = Student
        fields = ['title', 'content', 'moredata']

