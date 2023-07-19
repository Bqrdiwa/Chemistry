from django.db import models
from home.models import Student
from home.models import Plan
from django.utils import timezone
import os
from jdatetime import datetime
from pytz import timezone as Tz

# Create your models here.

class Exam(models.Model):
    grad = [('دهم','دهم'),('یازدهم','یازدهم'),('دوازدهم','دوازدهم'),('فارغ التحصیل','فارغ التحصیل')]
    subjec = [('اول','فصل اول'),('دوم','فصل دوم'),('سوم','فصل سوم'), ('چهارم', 'فصل چهارم')]

    name = models.CharField(max_length=16)
    grade = models.CharField(max_length=16,choices=grad,null=True)
    unit = models.CharField(max_length=16,choices=subjec, null=True)
    time = models.IntegerField(default=40)
    date = models.CharField(max_length=48, default='')
    startTime = models.TimeField(default=timezone.now)
    endTime = models.TimeField(default=timezone.now)
    plans = models.ManyToManyField(Plan)
    status = models.CharField(default='None', max_length=16)
    
    
    Stime = models.CharField(max_length=254,default='',blank=True)
    def endAllExams(self):
        self.status = 'Ended'
        self.save()
        
    def makeResultFromAir(self, data):
            AIR = data['air']
            timeSpended = data['remaining']
            user = data['user']
            
            
            key = AIR.key
            key = key.split(',')
            questions = self.get_all_questions
            
            corrects = 0
            wrongs = 0
            not_answered = 0
            
            wrongs_pk = ''
            corrects_pk = ''
            not_answered_pk = ''

            result_key = ''
            for index,choice in enumerate(key):
                question = questions[index]
                answer = question.Answer
                if choice == answer:
                    corrects_pk += str(question.pk)+','
                    corrects += 1
                elif choice == '0':
                    not_answered_pk += str(question.pk)+','
                    not_answered += 1
                else:
                    wrongs += 1
                    wrongs_pk += str(question.pk)+','
                result_key+=choice
            wrongs_pk = wrongs_pk[:-1]
            corrects_pk = corrects_pk[:-1]
            not_answered_pk = not_answered_pk[:-1]
            percent = ((3 * corrects) - (wrongs))/(3*self.get_q_l)* 100
            percent = round(percent, 2)
            
            timeSpended = float(timeSpended)
            if timeSpended < 0:
                timeSpended = 0


            result = Result.objects.create(Answers = result_key,
                                  timeSpended = timeSpended,
                                  percent = percent,
                                  wrongs= wrongs,
                                  corrects = corrects,
                                  notAnswered = not_answered,
                                  Exam_related = self,
                                  participant = user,
                                  wrongs_link = wrongs_pk,
                                  corrects_link = corrects_pk,
                                  notAnswered_link = not_answered_pk
                                  )
            AIR.delete()
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
    def get_all_airs(self):
        return ExamAir.objects.filter(Exam_related = self)
    def __str__(self):
        return self.name

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


class ExamAir(models.Model):
    key = models.CharField(max_length=2000,default='')
    student_related = models.ForeignKey(Student, on_delete=models.CASCADE)
    Exam_related = models.ForeignKey(Exam, on_delete=models.CASCADE, null=True)
    startTime = models.CharField(default='None',max_length=128)
class Result(models.Model):
    Answers = models.CharField(max_length=320)
    timeSpended = models.CharField(max_length=128,null=True)
    percent = models.FloatField()
    wrongs = models.CharField(max_length=128)
    corrects = models.CharField(max_length=128)
    notAnswered = models.CharField(max_length=128,null=True)
    Exam_related = models.ForeignKey(Exam,on_delete=models.CASCADE)
    participant = models.ForeignKey(Student,on_delete=models.CASCADE)
    dateSubmited = models.DateTimeField(default=timezone.now)
    
    wrongs_link = models.CharField(max_length=400,null=True)
    corrects_link = models.CharField(max_length=400,null=True)
    notAnswered_link =models.CharField(max_length=400,null=True)

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
        localtimezone = Tz('Asia/Tehran')
        endate = self.date_created.astimezone(localtimezone)
        fadate = datetime.fromgregorian(datetime = endate).strftime('%Y-%m-%d')
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