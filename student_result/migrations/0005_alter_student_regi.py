# Generated by Django 3.2.19 on 2023-06-24 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student_result', '0004_auto_20230624_1925'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='regi',
            field=models.CharField(max_length=15, unique=True),
        ),
    ]