# Generated by Django 4.1.5 on 2023-12-25 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0014_alter_productimage_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_error',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
