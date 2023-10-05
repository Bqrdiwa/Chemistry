from django.db import models
from home.models import Student
from home.models import Plan
from django.utils import timezone
import os
import jdatetime
from django import forms
import pytz
from datetime import datetime, timedelta
from django.utils import timezone
from jalali_date.fields import JalaliDateField
from jalali_date.widgets import AdminJalaliDateWidget

# Create your models here.

class Exam(models.Model):
    grad = [('دهم','دهم'),('یازدهم','یازدهم'),('دوازدهم','دوازدهم'),('فارغ التحصیل','فارغ التحصیل')]
    subjec = [('اول','فصل اول'),('دوم','فصل دوم'),('سوم','فصل سوم'), ('چهارم', 'فصل چهارم')]

    name = models.CharField(max_length=32, unique=True)
    grade = models.CharField(max_length=16,choices=grad,null=True)
    unit = models.CharField(max_length=16,choices=subjec, null=True)
    time = models.IntegerField(default=40)
    sdate = models.DateField(default=timezone.now)
    stime = models.TimeField(default=timezone.now)
    exampdf = models.FileField(upload_to='examPDFS',default='')
    plans = models.ManyToManyField(Plan)
    @property
    def get_q_l(self):
        return self.question_set.count()

    @property
    def get_all_questions(self):
        return Question.objects.filter(exam_related= self)

    @property
    def get_all_results(self):
        return Result.objects.filter(Exam_related = self)
    
    @property
    def status(self):
        tehran_time_zone = pytz.timezone('Asia/Tehran')
        examEndTime = (datetime.combine(self.sdate, self.stime) + timedelta(minutes=self.time)).astimezone(tehran_time_zone)
        nowTime = timezone.now().astimezone(tehran_time_zone)
        td = (examEndTime - nowTime).total_seconds()

        if td < 0:
            return 'Ended'
        elif td-300 > self.time*60:
            return 'None'
        else:
            return 'Started'

    def __str__(self):
        return self.name

class CreateExamForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateExamForm, self).__init__(*args, **kwargs)
        # self.fields['date'] = JalaliDateField(label=_('date'), # date format is  "yyyy-mm-dd"
        #     widget=AdminJalaliDateWidget # optional, to use default datepicker
        # )

        # you can added a "class" to this field for use your datepicker!
        # self.fields['date'].widget.attrs.update({'class': 'jalali_date-date'})

        self.fields['sdate'] = JalaliDateField(
            widget=AdminJalaliDateWidget # required, for decompress DatetimeField to JalaliDateField and JalaliTimeField
        )
    class Meta():
        model = Exam
        fields = ['name', 'grade', 'unit', 'time', 'sdate', 'exampdf','stime']

class Question(models.Model):
    grad = [('',''),('دهم','دهم'),('یازدهم','یازدهم'),('دوازدهم','دوازدهم'),('فارغ التحصیل','فارغ التحصیل')]
    fasl = [('',''),('اول','فصل اول'),('دوم','فصل دوم'),('سوم','فصل سوم'),('چهارم','فصل چهارم')]
    Choice = [('1','گزینه اول'),('2','گزینه دوم'),('3','گزینه سوم'),('4','گزینه چهارم')]
    exam_related = models.ForeignKey(Exam,on_delete=models.CASCADE, null=True, blank=True)
    Question = models.ImageField(default='default.png',upload_to='questions_pics')
    Answer = models.CharField(max_length=1,choices=Choice,default=0)
    Grade  = models.CharField(max_length=16,choices=grad,default='')
    Unit = models.CharField(max_length=16,choices = fasl,default='')
    
    difficulty = models.CharField(max_length=48, default='50,1')
    voting = models.ManyToManyField(Student, blank=True)
    
    date_submited = models.DateTimeField(default=timezone.now)
    @property
    def get_solution(self):
        try:
            return Question_Solution.objects.get(questionRelated = self)
        except:
            return False
    def difficulty_add(self, diff, student):
        main_diff, counter = self.difficulty.split(',')

        student_value = student.value
        counted_value = int(counter) + 1
        
        main_diff = int((int(main_diff)  + int(diff)*student_value) /( student_value + 1))
        print(diff, student_value)

        self.difficulty = str(main_diff) +','+ str(counted_value)
        self.save()
    def __str__(self):
        return '#'+str(self.pk)
class Question_Solution(models.Model):
    questionRelated = models.OneToOneField(Question, on_delete = models.CASCADE, default='')
    solution = models.FileField(default='default.png', upload_to='question-solution')
    date_submited = models.DateTimeField(default=timezone.now) 
    content = models.CharField(max_length=480)
    
    @property
    def get_file_type(self):
        extension = os.path.splitext(self.solution.name)[1][1:]

        if extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
            return 'image'
        elif extension in ['mp4', 'avi', 'mkv', 'mov', 'wmv']:
            return 'video'
        else:
            return 'unknown'

class Result(models.Model):
    Answers = models.CharField(max_length=320,default='')
    Exam_related = models.ForeignKey(Exam,on_delete=models.CASCADE)
    participant = models.ForeignKey(Student,on_delete=models.CASCADE)
    dateSubmited = models.DateTimeField(default=timezone.now)
    timeSpend = models.DurationField(null=True)

    @property
    def get_detail(self):
        ended = False
        if self.timeSpend != None:
            ended = True
        c = 0
        answeres = self.Answers.split(',')
        links = {
            'wl': [],
            'cl': [],
            'nl': []
        }
        for q in self.Exam_related.get_all_questions:
            if str(q.Answer) == answeres[c]:
                links['cl'].append(q.pk)
            elif answeres[c] == '0':
                links['nl'].append(q.pk)
            else:
                links['wl'].append(q.pk)
            c += 1
        percent = ((3*len(links['cl'])) - len(links['wl'])) / (3 * self.Exam_related.get_q_l) * 100
        percent = round(percent,2)
        return {
            'percent': percent,
            'links': links,
            'ended': ended
        }
    def __str__(self):
        return self.participant.username +' '+ self.Exam_related.name

class virtualExam(models.Model):
    time = models.PositiveIntegerField(default=20)
    questions = models.ManyToManyField(Question)
    filters = models.CharField(max_length=480)
    status = models.CharField(max_length=24)
    studentRelated = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    difficulty = models.CharField(max_length=10)
    date_created = models.DateTimeField(default=timezone.now)
    keys = models.CharField(max_length=200,default='', blank=True)

    @property
    def fastatus(self):
        status_list = {
            'not_started':'شروع نشده',
            'started':'شروع شده',
            'ended':'اتمام یافته'
        }
        
        return status_list[self.status]
    @property
    def get_filters(self):
        filters_list = []
        for filter in self.filters.split(','):
            if filter in ['دهم','یازدهم','دوازدهم']:
                filters_list.append(filter)
            else:
                filters_list.append('فصل '+filter)
        return filters_list
    
    @property 
    def get_date(self):
        localtimezone = pytz.timezone('Asia/Tehran')
        endate = self.date_created.astimezone(localtimezone)
        fadate = jdatetime.datetime.fromgregorian(datetime = endate).strftime('%Y-%m-%d')
        return fadate
    
    @property
    def questions_count(self):
        return self.questions.all().count()
    
    @property
    def result(self):
        if self.status == 'ended':
            key = self.keys.split(',')
            corrects_pk = []
            wrongs_pk = []
            not_answered_pk = []
            for index, question in enumerate(self.questions.all()):
                if question.Answer == key[index]:
                    corrects_pk.append(question.pk)
                elif key[index] == '0':
                    not_answered_pk.append(question.pk)
                else: 
                    wrongs_pk.append(question.pk)
            percent = ((3 * len(corrects_pk)) - len(wrongs_pk))/(3*self.questions_count)*100
            percent = round(percent, 2)
            return {
                'percent':percent,
                'wrongs': len(wrongs_pk),
                'corrects': len(corrects_pk),
                'not_answered': len(not_answered_pk),
                'not_anwered_pk': not_answered_pk,
                'corrects_pk': corrects_pk,
                'wrongs_pk': wrongs_pk, 
            }
        else:
            return None