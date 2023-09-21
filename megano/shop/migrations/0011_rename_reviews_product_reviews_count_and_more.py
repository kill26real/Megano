# Generated by Django 4.1.5 on 2023-09-08 16:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0010_alter_product_rating'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='reviews',
            new_name='reviews_count',
        ),
        migrations.RemoveField(
            model_name='category',
            name='categories',
        ),
        migrations.CreateModel(
            name='Subcategory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=40)),
                ('archived', models.BooleanField(default=True)),
                ('slug', models.SlugField(max_length=40)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.category')),
                ('products', models.ManyToManyField(related_name='subcategories', to='shop.product')),
            ],
        ),
    ]