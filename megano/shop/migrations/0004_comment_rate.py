# Generated by Django 4.1.5 on 2023-09-02 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_remove_product_img_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='rate',
            field=models.IntegerField(default=10),
        ),
    ]
