# Generated by Django 2.1.5 on 2019-09-05 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0009_auto_20190822_0218'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='formalized_title',
            field=models.CharField(max_length=255, null=True, verbose_name='Формализованные данные'),
        ),
    ]
