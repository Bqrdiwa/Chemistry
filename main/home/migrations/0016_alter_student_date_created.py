# Generated by Django 4.2 on 2023-05-30 12:49

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0015_remove_solution_likes_solutionlike'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
