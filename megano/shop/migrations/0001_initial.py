# Generated by Django 4.1.5 on 2023-12-07 22:39

import datetime
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('manage', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=40)),
                ('archived', models.BooleanField(default=True)),
                ('slug', models.SlugField(max_length=40)),
            ],
            options={
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('payment_type', models.CharField(choices=[('V', 'Visa'), ('MC', 'MasterCard'), ('PP', 'PayPal'), ('AE', 'AmericanExpress'), ('E', 'Electron'), ('M', 'Maestro'), ('D', 'Delta'), ('C', 'Cash'), ('QR', 'QR-Code'), ('O', 'Online')], max_length=20)),
                ('city', models.CharField(blank=True, max_length=40)),
                ('address', models.CharField(blank=True, max_length=100)),
                ('promocode', models.CharField(blank=True, max_length=20)),
                ('delivery_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='manage.deliverytype')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ('count', models.IntegerField(default=0)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(max_length=40)),
                ('full_description', models.TextField(blank=True)),
                ('sold_amount', models.IntegerField(default=0)),
                ('limited', models.BooleanField(default=0)),
                ('free_delivery', models.BooleanField(default=0)),
                ('slug', models.SlugField(max_length=40)),
                ('sale_price', models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ('date_from', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('date_to', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='products', to='shop.category')),
            ],
            options={
                'verbose_name': 'product',
                'ordering': ['title', 'price'],
            },
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
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('rate', models.IntegerField(default=5, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='shop.product')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.AddField(
            model_name='product',
            name='specifications',
            field=models.ManyToManyField(related_name='products', to='shop.specification'),
        ),
        migrations.AddField(
            model_name='product',
            name='tags',
            field=models.ManyToManyField(related_query_name='products', to='shop.tag'),
        ),
        migrations.AddField(
            model_name='category',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='subcategories', to='shop.category'),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(null=True)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('code', models.IntegerField(null=True)),
                ('paid', models.BooleanField(default=0)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='shop.order')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.PositiveSmallIntegerField(default=0)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='shop.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='shop.product')),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('src', models.ImageField(upload_to='files/')),
                ('alt', models.CharField(blank=True, max_length=100)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'unique_together': {('content_type', 'object_id')},
            },
        ),
    ]
