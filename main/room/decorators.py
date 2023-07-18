from django.shortcuts import redirect
from .models import room
from django.contrib import messages
def room_exist(view_func):
    def wrapper(request, roomName, *args, **kwargs):
        go = True
        admi = False

        if request.user.groups.filter(name='Admin').count() > 0 :
            admi = True
        try:
            ROOM = room.objects.get(Room_title = roomName)
            if not ROOM.enable and (not admi):
                go = f'کلاس مورد نظرشما هنوز شروع نشده'
            perm = False
            userGroups = request.user.plans.all()
            for g in ROOM.plan.all():
                if g in userGroups:
                    perm = True
                    break
            if not perm:
                plans = ''
                for plan in ROOM.plan.all():
                    plans += plan.name +' ,'
                plans = plans[:-1]
                planha = '<a href="/plans/">پلن ها</a>'
                go = f' شما برای ورود به این کلاس باید حداقل یکی از پلن های {plans} را داشته باشید .{planha}'
        except:
            go = f'کلاسی با نام {roomName} هنوز ساخته نشده است'
        if go == True:
            return view_func(request, roomName, *args, **kwargs)
        else:
            messages.success(request, go)
            return redirect('room-lobby')
    return wrapper  