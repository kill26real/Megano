# Generated by Django 4.1.5 on 2023-09-09 21:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0015_alter_product_price_alter_sale_new_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='products',
            field=models.ManyToManyField(related_name='categories', to='shop.product'),
        ),
    ]
