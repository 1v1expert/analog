# Generated by Django 2.2.10 on 2020-08-20 00:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0022_auto_20200710_1555'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='analogs_to',
            field=models.ManyToManyField(related_name='_product_analogs_to_+', to='catalog.Product'),
        ),
    ]