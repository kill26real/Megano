# Generated by Django 4.1.5 on 2023-09-15 11:40

import computed_property.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0011_remove_basket_items_basketitem_basket_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basket',
            name='total_sum',
            field=computed_property.fields.ComputedTextField(compute_from='calculation', editable=False),
        ),
    ]
