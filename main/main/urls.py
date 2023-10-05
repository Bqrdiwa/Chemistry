"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path , include
from authenticate import views as authenticate_views
from exam import views as exam_views
from django.conf import settings
from django.conf.urls.static import static
from video import views as video_view
from room import views as room_view
from django.conf.urls import handler404


handler404 = 'home.views.error_404'
handler400 = 'home.views.error_400'
handler403 = 'home.views.error_403'
handler500 = 'home.views.error_500'

urlpatterns = [
    path('chemadmin/', admin.site.urls),
    path('', include('home.urls')),
    path('login/', authenticate_views.Login,name='login'),
    path('register/',authenticate_views.Register,name='register'),
    path('logout/', authenticate_views.Logout,name='logout'),
    path('passwordreset/', authenticate_views.ForgotPassword, name='password-reset'),
    path('exam/', exam_views.exam,name='exam'),
    path('exam/<str:name>/', exam_views.exampage,name='exam-started'),
    path('exam/admin/<str:name>/', exam_views.AdminPanelAzmoon,name='exam-admin'),
    path('exam/<str:examName>/questions/', exam_views.examQuestions, name='exam-questions'),
    path('exam/result/<str:pk>/', exam_views.Javab,name='exam-result'),
    path('exam/result/<str:pk>/Questions/', exam_views.Javab_questions,name='exam-result-questions'),
    path('profile/',authenticate_views.Profile,name= 'profile'),
    path('video/',video_view.video,name = 'video-list'),
    path('video/<str:pk>',video_view.video_detail,name='video-detail'),
    path('video/watchlist/<str:username>/',video_view.saved_video,name='video-watchlist'),
    path('class/',room_view.lobby,name='room-lobby'),
    path('class/<str:roomName>',room_view.room_view,name='room-lobby'),
    path('create/exam/', exam_views.create, name='exam-create'),
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
