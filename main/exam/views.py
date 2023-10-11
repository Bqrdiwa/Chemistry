from django.shortcuts import render,redirect
from .models import Exam, Result, Question, CreateExamForm
from json import dumps
from django.http import JsonResponse
from .decorators import result_permission, exam_permission
from home.decorators import AdminRights
from django.core.paginator import Paginator, PageNotAnInteger
from django.contrib.auth.decorators import login_required 
from home.decorators import BasePlanReq
import pytz
import jdatetime
from home.models import Plan
from datetime import datetime, timedelta
from django.utils import timezone
# Create your views here.
@login_required
@BasePlanReq
def exam(request):
    context = {'title':'Exams','HT':'آزمون ها'}

    Exams = Exam.objects.all()
    allExams = []
    AvailableExams = []
    DuringExams = []
    ResultExams = []

    for exam in Exams:
        tehran_time_zone = pytz.timezone('Asia/Tehran')
        examEndTime = (datetime.combine(exam.sdate, exam.stime) + timedelta(minutes=exam.time)).astimezone(tehran_time_zone)
        nowTime = timezone.now().astimezone(tehran_time_zone)
        td = (examEndTime - nowTime).total_seconds()
        if td < 0:
            allExams.append(
                {
                    'exam': exam,
                    'status': 'برگذار شده'
                }
            )
            try:
                result = Result.objects.get(Exam_related= exam, participant = request.user)
                ResultExams.append(result)
            except:pass
        elif td-1800 > exam.time*60:
            allExams.append(
                {
                    'exam': exam,
                    'status': 'برگزار نشده'
                }
            )
        else:
            allExams.append(
                {
                    'exam': exam,
                    'status': 'در حال اجرا'
                }
            )
            try:
                result = Result.objects.get(Exam_related= exam, participant = request.user)
                if result.timeSpend != None:
                    ResultExams.append(result)
                else:
                    DuringExams.append(exam)
            except:
                AvailableExams.append(exam)
        # if exam.status == 'Started':
        #     allExams.append({
        #         'exam':exam,
        #         'status':'در حال اجرا ...',
        #     })
        #     try:
        #         examDuring = ExamAir.objects.get(Exam_related = exam, student_related = request.user)
        #         key = examDuring.key.split(',')
        #         counter = 0
        #         for item in key:
        #             if item != '0':
        #                 counter += 1
        #         progress_percent = int(counter / exam.get_q_l * 100)
        #         DuringExams.append({
        #             'name':exam.name,
        #             'progress':str(progress_percent),
        #             'pk':exam.pk
        #         })
        #     except:
        #         try:
        #             result = Result.objects.get(participant = request.user, Exam_related= exam)
        #             ResultExams.append(result)
        #         except:
        #             AvailableExams.append(exam)
        # elif exam.status == 'None':
        #   allExams.append({
        #       'exam':exam,
        #       'status':'برگزار نشده'
        #   })
        # else:
        #     try:
        #         result = Result.objects.get(participant = request.user, Exam_related= exam)
        #         ResultExams.append(result)
        #     except:
        #         pass
        #     allExams.append({
        #         'exam':exam,
        #         'status':'برگزار شده'
        #     })
    detail = {}
    
    detail['examsCount']= Exams.count()
    detail['participantsCount'] = Result.objects.all().count() * 3
    detail['questionsCount']= Question.objects.all().count()
    context['availableExams'] = AvailableExams
    context['DuringExams'] = DuringExams
    context['ResultExams'] = ResultExams
    context['detail'] = detail
    print(detail)
    admi = False
    if request.user.groups.filter(name ='Admin').count()> 0:
        admi = True
    if admi:
        context['allExams'] = allExams
    context['admi'] = admi
    return render(request,'exam/exam.html',context=context)


@login_required
@exam_permission
@BasePlanReq
def exampage(request, name):
    context = {'title': name, 'HT':name}
    exam = Exam.objects.get(name=name)
    if request.method == 'POST':
        action = request.POST['action']
        rs = Result.objects.get(Exam_related = exam, participant= request.user)
        if action == 'updateKey':
            rs.Answers = request.POST['key']
            rs.save()
        elif action == 'endExam':
            tehran_time_zone = pytz.timezone('Asia/Tehran')
            startofexam = datetime.combine(exam.sdate, exam.stime).astimezone(tehran_time_zone)
            nowT = timezone.now().astimezone(tehran_time_zone)
            rs.timeSpend = nowT - startofexam
            rs.save()
            context['resultPk'] = rs.pk
        return JsonResponse(context)
    questions_of_exam = []
    c = 0
    for q in exam.get_all_questions:
        questions_of_exam.append(
            {
                'ID': q.pk,
                'image': q.Question.url,
                'number': c
            }
        )
        c += 1
    default_answer = ('0,'*exam.get_q_l)[:-1]
    result, _ = Result.objects.get_or_create(participant= request.user,
                                              Exam_related = exam)
    if _:
        result.Answers = default_answer
        result.save()
    print(result.timeSpend)
    startofexam = datetime.combine(exam.sdate, exam.stime)
    endofexam =  startofexam + timedelta(minutes=exam.time)
    tehran_time_zone = pytz.timezone('Asia/Tehran')
    endT =endofexam.astimezone(tehran_time_zone)
    nowT = timezone.now().astimezone(tehran_time_zone)
    context['KEY'] = result.Answers
    context['remainT'] = int((endT - nowT).total_seconds())
    context['questions'] = questions_of_exam
    context['exam'] = exam
    return render(request, 'exam/exampage.html', context)
@login_required
@AdminRights
def AdminPanelAzmoon(request, name):
    context = {}
    exam = Exam.objects.get(name = name)

    qls = []
    inde =0
    for q in exam.get_all_questions:
        inde += 1
        qls.append({
            'number': inde,
            'a': q.Answer
        })
    cleaned_results =[]
    results = Result.objects.filter(Exam_related = exam)
    for r in results:
        rdetail = r.get_detail
        cleaned_results.append({
            'pk':r.pk,
            'examname': r.Exam_related.name,
            'percent': rdetail.get('percent'),
            'ended': rdetail.get('ended'),
            'participant':r.participant.username
        })
    sorted_data = sorted(cleaned_results, key=lambda x: x['percent'], reverse=True)
    context['results'] = sorted_data
    context['rc'] = len(sorted_data) * 3
    context['exam'] = exam
    context['qls'] = qls
    return render(request, 'exam/examadminpanel.html', context)

@result_permission
@login_required
@BasePlanReq
def Javab(request, pk):
    my_result = Result.objects.get(pk = pk)
    examRelated = my_result.Exam_related
    all_of_my_results = Result.objects.filter(participant = my_result.participant)
    timeSpend = my_result.timeSpend.total_seconds()
    timespend_on_every_q = timeSpend / examRelated.get_q_l
    details = my_result.get_detail

    all_of_results = []
    mins = int(timeSpend // 60)
    secs = int(timeSpend % 60)
    if mins< 10:
        mins = '0' + str(int(mins))
    if secs < 10 :
        secs = '0'+ str(secs)
    timeSpendForExam = str(mins)+':'+str(secs)
    for r in all_of_my_results:
        ttz = pytz.timezone('Asia/Tehran')
        examTime = r.Exam_related.sdate
        persianTime = jdatetime.datetime.fromgregorian(datetime = examTime)
        all_of_results.append(
            {
                'ExamName':r.Exam_related.name,
                'date': persianTime.strftime('%Y/%m/%d'),
                'timespend': round((r.timeSpend.total_seconds() / r.Exam_related.get_q_l),2),
                'percent': r.get_detail['percent'],

            }
        )
    context = {'title':'Result',
                'HT':'نتایج',
                'exam': examRelated,
                'participants_count': Result.objects.filter(Exam_related = examRelated).count() * 3,
                'result': my_result,
                'TSOEQ': round(timespend_on_every_q,2),
                'percent' : details['percent'],
                'corrects_c': len(details['links']['cl']),
                'wrongs_c': len(details['links']['wl']),
                'not_answered_c': len(details['links']['nl']),
                'timeSpendForExam': timeSpendForExam,
                'all_results': dumps(all_of_results)
                }
    

    
    return render(request,'exam/result.html',context)
    
        

@login_required
@BasePlanReq
def Javab_questions(request,pk):
    result = Result.objects.get(pk=pk)
    detail = result.get_detail
    wrongs_list = detail['links']['wl']
    corrects_list = detail['links']['cl']
    notAnswered_list = detail['links']['nl']


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
    if request.method == 'POST':
        form = CreateExamForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            planpaye = Plan.objects.get(name = 'پایه')
            exam = Exam.objects.get(name = request.POST['name'])
            exam.plans.add(planpaye)
            exam.save()

            return redirect('exam')
        else:
            print(form.errors)
    form = CreateExamForm()
    context['form'] = form
    return render(request, 'exam/create.html', context)
    