# Generated by Django 4.1.5 on 2023-12-07 22:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('free_delivery', models.DecimalField(decimal_places=2, default=2000, max_digits=11)),
            ],
        ),
    ]
