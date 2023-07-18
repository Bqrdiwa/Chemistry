from django.shortcuts import render
from django.views.generic import ListView, DetailView, View
from .models import  Video, WatchList
from django.http import JsonResponse
import json
from django.core import serializers
from django.db.models import Q
from functools import reduce
from django.contrib.auth.decorators import login_required 

# Create your views here.
@login_required 
def video(request):
    context = {'title':'Video','HT':'ویدیو'}
    if request.method =='POST':
        filters = json.loads( request.POST['filters'])
        
        videos = Video.objects.all()
        filterRawGrade = []
        filterRawUnit = []

        
        for filter in filters:
            if filter in ['دهم','دوازدهم','یازدهم']:
                filterRawGrade.append(Q(grade = filter))
            else:
                filterRawUnit.append(Q(Unit=filter))
        filtered1 = Video.objects.none()
        filtered1 = reduce(lambda qs, f: qs | Video.objects.filter(f), filterRawUnit, filtered1)
        filtered2 = Video.objects.none()
        filtered2 = reduce(lambda qs, f: qs | Video.objects.filter(f), filterRawGrade, filtered2)
        
        videos = filtered1.union(filtered2)   
        if filters  == []: videos = Video.objects.all()  
        context['videos'] =  serializers.serialize('json',videos)
        videosDuration = []
        if videos.count() == 0:
            context['videos'] = 'None'

        for vid in videos:
            videosDuration.append(vid.get_video_duration())
        context['duration'] = videosDuration
        return JsonResponse(context)
    else:
        videos = Video.objects.all()
        context['videos'] = videos
        return render(request,'video/video.html',context)

@login_required 
def video_detail(request,pk):
    watchlist = WatchList.objects.get(userRelated=request.user)
    
    if request.method == 'POST':
        video = Video.objects.get(pk=pk)
        
        if video in watchlist.videos.all():
            watchlist.videos.remove(video)
            context={'message':'remove'}
        else:
            watchlist.videos.add(video)
            context={'message':'add'}
        
        return JsonResponse(context)
    else:
        video = Video.objects.get(pk=pk)
        grade = video.grade
        videos_related = Video.objects.all().filter(grade = grade)
        context = {'video':video,'videos_related':videos_related,'watchlist':watchlist.videos.all(),'title':'Video','HT':'ویدیو'}

        return render(request,'video/video_detail.html',context=context)
@login_required 
def saved_video(request,username):
    videos = WatchList.objects.get(userRelated = request.user).videos.all()
    count = videos.count()
    context = {'title':'WatchList','HT':'لیست پخش','videos':videos,'count':count}
    return render(request,'video/watchlist.html',context)
