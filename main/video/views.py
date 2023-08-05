from django.shortcuts import render
from django.views.generic import ListView, DetailView, View
from .models import  Video, WatchList
from django.http import JsonResponse
from json import loads, dumps
from django.core.paginator import Paginator
from home.decorators import BasePlanReq
from django.contrib.auth.decorators import login_required 

# Create your views here.
@login_required 
@BasePlanReq
def video(request):
    context = {'title':'Video','HT':'ویدیو'}
    if request.method =='POST':
        context['ERR'] = 'None'
        filters = loads(request.POST['filters']) 
        keys = filters.keys()
        grade_filters = []
        unit_filters = []
        type_filters = []

        type_translator  = {
            'درسنامه': 'درسنامه',
            'تست': 'نکته تست',
            'حل': 'دانش آموزان'
        }
        for item in keys:
            if item in ['دهم', 'یازدهم', 'دوازدهم'] and filters[item] == True:
                grade_filters.append(item)
            elif item in ['اول','دوم','سوم','چهارم'] and filters[item] == True:
                unit_filters.append(item)
            elif item in ['حل','تست','درسنامه'] and filters[item] == True:
                type_filters.append(type_translator[item])


        if not grade_filters :grade_filters = ['دهم', 'یازدهم', 'دوازدهم']
        if not unit_filters :unit_filters = ['اول','دوم','سوم','چهارم']
        if not type_filters :type_filters = ['دانش آموزان','نکته تست','درسنامه']
        filtered_videos = Video.objects.filter(
            grade__in = grade_filters
        ).filter(
            Unit__in = unit_filters
        ).filter(
            Type__in = type_filters
        )
        
        page_num = request.GET.get('page')
        paginator = Paginator(filtered_videos, 30)
        filtered_videos = paginator.get_page(page_num)
        videos_list = []

        pr = paginator.page_range
        page_ranges = []
        for i in pr :
            page_ranges.append(i)
        for video in filtered_videos:
            videos_list.append({
                'title': video.Title,
                'thumb': video.Thumbnail.url,
                'pk': video.pk
            })
        context['videos'] = dumps(videos_list)
        context['page_ranges'] = dumps(page_ranges)

        return JsonResponse(context)
    else:
        videos = Video.objects.all()
        page_num = request.GET.get('page')
        paginator = Paginator(videos, 30)
        videos = paginator.get_page(page_num)
        context['videos'] = videos
        return render(request,'video/video.html',context)

@login_required 
@BasePlanReq
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
@BasePlanReq
def saved_video(request,username):
    videos = WatchList.objects.get(userRelated = request.user).videos.all()
    count = videos.count()
    context = {'title':'WatchList','HT':'لیست پخش','videos':videos,'count':count}
    return render(request,'video/watchlist.html',context)
