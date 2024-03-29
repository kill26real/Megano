# Generated by Django 4.1.5 on 2023-12-17 11:44

from django.db import migrations, models
import user.models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_profile_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(blank=True, upload_to=user.models.profile_image_directory_path),
        ),
    ]
