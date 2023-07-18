from django.urls import path
from room.consumers import RoomConsumer
from exam.consumer import ExamConsumer

websocket_urlpatterns = [
    path('ws/exam/<str:examPK>/', ExamConsumer.as_asgi()),
    path('ws/<str:roomName>/', RoomConsumer.as_asgi())
]