# Generated by Django 4.1.5 on 2023-09-16 22:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0024_remove_orderitem_sum'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='total_cost',
        ),
    ]
