# Generated by Django 4.1.5 on 2023-12-15 09:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_rename_delivery_type_order_delivery'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='promocode',
        ),
    ]
