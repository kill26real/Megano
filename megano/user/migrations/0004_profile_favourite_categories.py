# Generated by Django 4.1.5 on 2023-09-05 09:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0007_alter_image_img'),
        ('user', '0003_alter_profile_e_mail'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='favourite_categories',
            field=models.ForeignKey(default=123, on_delete=django.db.models.deletion.PROTECT, to='shop.category'),
            preserve_default=False,
        ),
    ]