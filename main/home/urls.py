from django.urls import path
from .views import Home,  Announcement,Solution_view,informationBank,Solution_Not_Answered, Solution_Question_view, Question_view, Plans_view, Question_bank,virtualExamPage,  VirtualExam, virtualExamResultQuestions


urlpatterns = [
    
    path('',Home,name = 'home'),
    path('announcment/',Announcement,name= 'announcment'),
    path('solution/',Solution_view,name= 'solution'),
    path('solution/question-<str:pk>/', Solution_Question_view, name='solution-question'),
    path('solution/notanswered-questions/', Solution_Not_Answered, name='not-answered-questions'),
    path('plans/', Plans_view, name='plans'),
    path('questionbank/', Question_bank, name='question-bank'),
    path('questionbank/virtualexam/', VirtualExam, name='virtual-exam'),
    path('questionbank/<str:pk>/', Question_view, name='question-view'),
    path('questionbank/virtualexam/<str:pk>/', virtualExamPage, name='virtual-exam-page'),
    path('questionbank/virtualexam/<str:pk>/questions/', virtualExamResultQuestions, name='virtual-exam-questions'),
    path('informationbank/',informationBank,name='information-bank')
]

