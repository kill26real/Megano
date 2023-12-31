# Generated by Django 4.1.5 on 2023-09-08 14:27

import datetime
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('shop', '0007_alter_image_img'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('rate', models.IntegerField(default=5)),
                ('published_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-published_at'],
            },
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('old_price', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('new_price', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('date_from', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('date_to', models.DateTimeField(blank=True, default=datetime.datetime.now)),
            ],
        ),
        migrations.CreateModel(
            name='Specification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100)),
                ('value', models.CharField(blank=True, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=100)),
                ('object_id', models.PositiveIntegerField()),
            ],
        ),
        migrations.RemoveField(
            model_name='comment',
            name='product',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='user',
        ),
        migrations.RenameField(
            model_name='category',
            old_name='name',
            new_name='title',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='sort_index',
            new_name='amount',
        ),
        migrations.RemoveField(
            model_name='category',
            name='icon',
        ),
        migrations.RemoveField(
            model_name='image',
            name='product',
        ),
        migrations.RemoveField(
            model_name='order',
            name='payment_method',
        ),
        migrations.AddField(
            model_name='category',
            name='categories',
            field=models.ForeignKey(blank=True, default=123, on_delete=django.db.models.deletion.PROTECT, to='shop.category'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='category',
            name='slug',
            field=models.SlugField(default=123, max_length=40),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='image',
            name='content_type',
            field=models.ForeignKey(default=123, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='image',
            name='object_id',
            field=models.PositiveIntegerField(default=123),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='city',
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_type',
            field=models.CharField(choices=[('R', 'Regular'), ('E', 'Express'), ('F', 'Free')], default=123, max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='payment_type',
            field=models.CharField(choices=[('V', 'Visa'), ('MC', 'MasterCard'), ('PP', 'PayPal'), ('AE', 'AmericanExpress'), ('E', 'Electron'), ('M', 'Maestro'), ('D', 'Delta'), ('C', 'Cash'), ('QR', 'QR-Code'), ('O', 'Online')], default=123, max_length=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AddField(
            model_name='order',
            name='total_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
        ),
        migrations.AddField(
            model_name='product',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='free_delivery',
            field=models.BooleanField(default=0),
        ),
        migrations.AddField(
            model_name='product',
            name='rating',
            field=models.DecimalField(decimal_places=1, default=0, max_digits=1),
        ),
        migrations.AddField(
            model_name='product',
            name='reviews',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='product',
            name='slug',
            field=models.SlugField(default=123, max_length=40),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='category',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='image',
            name='img',
            field=models.ImageField(upload_to='files/'),
        ),
        migrations.AlterField(
            model_name='order',
            name='delivery_adress',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='order',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
