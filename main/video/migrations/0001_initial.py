# Generated by Django 4.1.4 on 2023-04-03 21:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Title', models.CharField(max_length=128)),
                ('Description', models.CharField(default='', max_length=320)),
                ('grade', models.CharField(choices=[('', ''), ('دهم', 'دهم'), ('یازدهم', 'یازدهم'), ('دوازدهم', 'دوازدهم')], default='', max_length=16)),
                ('Unit', models.CharField(choices=[('', ''), ('اول', 'اول'), ('دوم', 'دوم'), ('سوم', 'سوم')], default='', max_length=16)),
                ('File', models.FileField(upload_to='videos')),
                ('Thumbnail', models.ImageField(default='default.png', upload_to='video_thumbnail')),
            ],
        ),
        migrations.CreateModel(
            name='WatchList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userRelated', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('videos', models.ManyToManyField(to='video.video')),
            ],
        ),
    ]
