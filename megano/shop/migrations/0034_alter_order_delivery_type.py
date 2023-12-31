# Generated by Django 4.1.5 on 2023-09-23 20:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('manage', '0001_initial'),
        ('shop', '0033_alter_review_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='manage.deliverytype'),
        ),
    ]
