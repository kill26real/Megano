# Generated by Django 4.1.5 on 2023-09-03 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0006_image_alt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='img',
            field=models.ImageField(upload_to='images_products/None/'),
        ),
    ]
