# Generated by Django 4.1.5 on 2023-10-20 19:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0042_rename_new_price_sale_price_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='delivery_adress',
            new_name='address',
        ),
    ]
