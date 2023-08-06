from django.db import models
from home.models import Student
from PIL import Image

# Create your models here.
class Video(models.Model):
    grad = [('دهم','دهم'),('یازدهم','یازدهم'),('دوازدهم','دوازدهم')]
    fasl = [('اول','فصل اول'),('دوم','فصل دوم'),('سوم','فصل سوم'),('چهارم','فصل چهارم')]
    types = [('دانش آموزان','حل تست به همراهی دانش آموزان'),('نکته تست','نکته تست'),('درسنامه','درسنامه')]
    
    Title = models.CharField(max_length=128)
    Description = models.CharField(max_length=320,default='')

    Type = models.CharField(max_length=12,choices= types,default='')
    grade = models.CharField(max_length=16,choices=grad,default='')
    Unit = models.CharField(max_length=16,choices=fasl,default='')
    
    url = models.CharField(max_length=4000,default='')
    Thumbnail = models.ImageField(upload_to='video_thumbnail' ,default='default.png')
    
    def __str__(self):
        return self.Title
    
    def save(self, *args, **kwargs):
        super(Video,self).save(*args, **kwargs)
        if self.Thumbnail.size > 5048576:
            max_size = (1024, 1024)
            image_path = self.Thumbnail.path
            image = Image.open(image_path)
            image.thumbnail(max_size, Image.ANTIALIAS)
            image.save(image_path)
            
        

class WatchList(models.Model):
     userRelated = models.ForeignKey(Student,on_delete=models.CASCADE)
     videos = models.ManyToManyField(Video)
     
     def __str__(self):
         return self.userRelated.username+"'s WatchList"
     
