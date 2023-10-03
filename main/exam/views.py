from django.shortcuts import render,redirect
from .models import Exam, Result, Question, ExamAir
from json import dumps
from django.http import JsonResponse
from .decorators import result_permission, exam_permission
from django.core.paginator import Paginator, PageNotAnInteger
from django.contrib.auth.decorators import login_required 
from home.decorators import BasePlanReq
from pytz import timezone
from jdatetime import datetime
# Create your views here.
@login_required
def exam(request):
    context = {'title':'Exams','HT':'آزمون ها'}

    Exams = Exam.objects.all()
    allExams = []
    AvailableExams = []
    DuringExams = []
    ResultExams = []

    for exam in Exams:
        if exam.status == 'Started':
            allExams.append({
                'exam':exam,
                'status':'در حال اجرا ...',
            })
            try:
                examDuring = ExamAir.objects.get(Exam_related = exam, student_related = request.user)
                key = examDuring.key.split(',')
                counter = 0
                for item in key:
                    if item != '0':
                        counter += 1
                progress_percent = int(counter / exam.get_q_l * 100)
                DuringExams.append({
                    'name':exam.name,
                    'progress':str(progress_percent),
                    'pk':exam.pk
                })
            except:
                try:
                    result = Result.objects.get(participant = request.user, Exam_related= exam)
                    ResultExams.append(result)
                except:
                    AvailableExams.append(exam)
        elif exam.status == 'None':
          allExams.append({
              'exam':exam,
              'status':'برگزار نشده'
          })
        else:
            try:
                result = Result.objects.get(participant = request.user, Exam_related= exam)
                ResultExams.append(result)
            except:
                pass
            allExams.append({
                'exam':exam,
                'status':'برگزار شده'
            })
    detail = {}
    
    detail['examsCount']= Exams.count()
    detail['participantsCount'] = Result.objects.all().count()+ ExamAir.objects.all().count()
    detail['questionsCount']= Question.objects.all().count()
    context['availableExams'] = AvailableExams
    context['DuringExams'] = DuringExams
    context['ResultExams'] = ResultExams
    context['detail'] = detail
    print(detail)
    admi = False
    if request.user.groups.filter(name ='Admin').count()> 0 :
        admi = True
    if admi:
        context['allExams'] = allExams
    context['admi'] = admi
    return render(request,'exam/exam.html',context=context)

@exam_permission
@login_required
@BasePlanReq
def Azmoon(request, name):
    azmoon = Exam.objects.get(name=name)
    EXAM_STATUS = azmoon.status

    context = {'title':'Exam','HT':'آزمون'}
    

    admi_perm = False
    context['admin'] = False
    if request.user.groups.filter(name ='Admin').count() > 0:
        admi_perm= True
        context['admin'] = True
    
    context['Exam'] = azmoon
    
    if admi_perm:
        questions_list = []
        qC = 1
        for question in azmoon.get_all_questions:
            current_answer = [False,False,False,False]
            current_answer[int(question.Answer)-1]=True
            questions_list.append({
                'pk':qC,
                'choices':current_answer
            })
            qC += 1
        context['Questions'] = questions_list

        results = []
        students_count = 0
        for result in azmoon.get_all_results:
            students_count += 1
            results.append({
                'progress':'ended',
                'name':result.participant.get_name,
                'grade': result.participant.grade,
                'subject': result.participant.subject,
                'percent': result.percent,
                'pk':result.participant.pk,
                'resultPk':result.pk
            })
        for air in azmoon.get_all_airs:
            key = air.key.split(',')
            students_count += 1
            answered = 0
            for item in key:
                if item != '0':
                    answered += 1
            progressPercent = answered / len(key) * 100
            results.append({
                'progress':progressPercent,
                'name':air.student_related.get_name,
                'pk':air.student_related.pk
            })
        context['studens_progress'] = results
        context['students_count']=students_count
    else:
        numed_questions = []
        c = 1
        for i in  azmoon.get_all_questions:
            i.question_number = c
            c += 1
            numed_questions.append(i)
        context['Questions'] =numed_questions
    if admi_perm or EXAM_STATUS == 'Started':
        if not admi_perm:
            air, created = ExamAir.objects.get_or_create(student_related=request.user, Exam_related = azmoon)
            context['AIR'] = {'key':air.key,'start':air.startTime}
        return render(request,'exam/azmoon.html',context)
    else:
        return redirect('exam')


@result_permission
@login_required
@BasePlanReq
def Javab(request, pk):
    my_result = Result.objects.get(pk = pk)
    examRelated = my_result.Exam_related
    all_of_my_results = Result.objects.filter(participant = my_result.participant)

    avg_percent = 0
    student_counter = 0
    avg_time = 0

    for result in examRelated.get_all_results:
        avg_percent += float(result.percent)
        avg_time += float(result.timeSpended)
        student_counter += 1
    
    avg_percent /= student_counter
    avg_time /= (student_counter * examRelated.get_q_l)

    avg_percent = round(avg_percent, 2)
    avg_time = round(avg_time, 2)

    your_percent = my_result.percent
    your_time = float(my_result.timeSpended) / examRelated.get_q_l

    your_time = round(your_time, 2)

    spending_time = float(my_result.timeSpended)
    smins = int(spending_time // 60)
    ssecs = int(spending_time - (60 * smins))
    if (smins < 10):
        smins = '0' + str(smins)
    if(ssecs < 10):
        ssecs = '0'+ str(ssecs)
    spending_time = f'{str(smins)}:{str(ssecs)}'

    all_results_list = []
    tehran_time_zone = timezone('Asia/Tehran')
    for result in all_of_my_results:
        date = result.dateSubmited
        date = date.astimezone(tehran_time_zone)
        pdt = datetime.fromgregorian(datetime = date)
        time = pdt.strftime('%Y/%m/%d')

        timespend = float(result.timeSpended)
        timespend /= result.Exam_related.get_q_l
        timespend = round(timespend,2)
        all_results_list.append({
            'ExamName':result.Exam_related.name,
            'date':time,
            'timespend':timespend,
            'percent':result.percent
            
        })
    scoreBoard = Result.objects.filter(Exam_related = examRelated).order_by('-percent')[:4]
    context = {'title':'Result',
                'HT':'نتایج',
                'exam':examRelated,
                'my_result':{'percent':your_percent,
                             'your_time':your_time,
                             'your_spending':spending_time,
                             'corrects':my_result.corrects,
                             'wrongs':my_result.wrongs,
                             'not_answered':my_result.notAnswered,
                             'pk':my_result.pk
                             },
                'avg_result':{'percent':avg_percent,'time':avg_time},
                'all_results':dumps(all_results_list),
                'scoreboard':scoreBoard
                }
    

    
    return render(request,'exam/result.html',context)
    
        

@login_required
@BasePlanReq
def Javab_questions(request,pk):
    result = Result.objects.get(pk=pk)
    wrongs_list = result.wrongs_link.split(',')
    corrects_list = result.corrects_link.split(',')
    notAnswered_list = result.notAnswered_link.split(',')


    wrongs_q = []
    corrects_q = []
    notAnswered_q = []

    for i in wrongs_list:
        if i!='':wrongs_q.append(Question.objects.get(pk=i))
    for i in corrects_list:
        if i !='':corrects_q.append(Question.objects.get(pk=i))
    for i in notAnswered_list:
        if i != '':notAnswered_q.append(Question.objects.get(pk=i))

    return render(request,'exam/result_questions.html',context={'title':'Questions',
                                                                'HT':'سوالات آزمون',
                                                                'wrongs':wrongs_q,
                                                                'corrects':corrects_q,
                                                                'notAnswered':notAnswered_q
                                                                })
@login_required
@BasePlanReq
def examQuestions(request, examName):

    exam =Exam.objects.get(name = examName)

    questions = exam.get_all_questions

    paginator = Paginator(questions, 10)

    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    
    context = {'questions' : page_obj, 'title':'Questions', 'HT':'سوالات', 'Exam':exam}
    return render(request, 'exam/exam_questions.html', context= context)
@login_required
def create(request):
    context = {'title':'CreateExam','HT':'ساخت آزمون'}
    return render(request, 'exam/create.html', context)
    