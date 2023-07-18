# Generated by Django 4.2 on 2023-07-13 17:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('exam', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='virtualexam',
            name='keys',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='virtualexam',
            name='studentRelated',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
