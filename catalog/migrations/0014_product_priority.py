# Generated by Django 2.1.5 on 2020-03-18 01:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0013_product_is_enabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='priority',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Приоритет'),
        ),
    ]
