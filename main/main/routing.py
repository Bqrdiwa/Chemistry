from django.urls import path
from exam.consumer import ExamConsumer

websocket_urlpatterns = [
    path('ws/exam/<str:examPK>/', ExamConsumer.as_asgi())
]