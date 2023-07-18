from django.shortcuts import render
from .decorators import room_exist
from .models import room, Schedule
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required
def lobby(request):
    context = {'title':'Class','HT':'کلاس'}
    schedules = Schedule.objects.all()
    context['schedule']= schedules
    context['room'] = room.objects.all().first()

    return render(request,'room/lobby.html',context)

@login_required
@room_exist
def room_view(request, roomName):
    ROOM = room.objects.get(Room_title=roomName)
    context = {'roomname':roomName, 'perm':'False'}
    if request.user.groups.all().filter(name='Admin').count() >= 1:
        context['perm'] = 'True'
    return render(request,'room/room.html',context)