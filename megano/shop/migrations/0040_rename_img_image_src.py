# Generated by Django 4.1.5 on 2023-10-20 00:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0039_alter_product_options_rename_name_product_title_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='image',
            old_name='img',
            new_name='src',
        ),
    ]
