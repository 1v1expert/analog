# Generated by Django 2.1.5 on 2019-04-01 00:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0005_auto_20190401_0032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datafile',
            name='file',
            field=models.FileField(upload_to='files', verbose_name='Файл'),
        ),
    ]