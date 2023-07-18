from django.shortcuts import redirect
from .models import WatchList

def watchList_perm(view_func):
    def wrapper(request,pk ,*args, **kwargs):
        if request.user == WatchList.objects.get():
            return view_func(request,pk ,*args,**kwargs)
            

        
    return wrapper

