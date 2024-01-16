# Generated by Django 4.1.5 on 2023-12-17 11:44

from django.db import migrations, models
import shop.models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0010_productimage_category_image_delete_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='image',
            field=models.ImageField(blank=True, upload_to=shop.models.category_image_directory_path),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='image',
            field=models.ImageField(blank=True, upload_to=shop.models.product_image_directory_path),
        ),
    ]
