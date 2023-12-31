# Generated by Django 4.1.5 on 2023-09-09 18:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0014_alter_category_options_alter_order_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9),
        ),
        migrations.AlterField(
            model_name='sale',
            name='new_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9),
        ),
        migrations.AlterField(
            model_name='sale',
            name='old_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9),
        ),
    ]
