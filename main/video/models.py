from django.db import models
from home.models import Student
from moviepy.video.io.VideoFileClip import VideoFileClip
from PIL import Image

# Create your models here.
class Video(models.Model):
    grad = [('',''),('دهم','دهم'),('یازدهم','یازدهم'),('دوازدهم','دوازدهم')]
    fasl = [('',''),('اول','فصل اول'),('دوم','فصل دوم'),('سوم','فصل سوم'),('چهارم','فصل چهارم')]
    
    Title = models.CharField(max_length=128)
    Description = models.CharField(max_length=320,default='')
    
    grade = models.CharField(max_length=16,choices=grad,default='')
    Unit = models.CharField(max_length=16,choices=fasl,default='')
    
    url = models.CharField(max_length=4000,default='')
    Thumbnail = models.ImageField(upload_to='video_thumbnail' ,default='default.png')
    
    def __str__(self):
        return self.Title
    
    def save(self, *args, **kwargs):
        super(Video,self).save(*args, **kwargs)
        
        with Image.open(self.Thumbnail.path) as img:
            resize = (1920,1080)
            img=  img.resize(resize)
            img.save(self.Thumbnail.path)
            
        

class WatchList(models.Model):
     userRelated = models.ForeignKey(Student,on_delete=models.CASCADE)
     videos = models.ManyToManyField(Video)
     
     def __str__(self):
         return self.userRelated.username+"'s WatchList"
     
