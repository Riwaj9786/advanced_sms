# Generated by Django 4.2.13 on 2024-06-06 06:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0004_alter_programcourse_teacher_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programcourse',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL),
        ),
    ]
