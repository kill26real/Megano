# Generated by Django 4.1.5 on 2023-09-16 11:49

import computed_property.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0021_remove_order_products_alter_order_total_cost_payment_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='total_cost',
            field=computed_property.fields.ComputedTextField(compute_from='calculat', editable=False),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='sum',
            field=computed_property.fields.ComputedTextField(compute_from='calculate', editable=False),
        ),
    ]
