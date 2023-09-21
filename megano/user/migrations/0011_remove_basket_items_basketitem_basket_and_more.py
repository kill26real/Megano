# Generated by Django 4.1.5 on 2023-09-15 09:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0019_alter_subcategory_category'),
        ('user', '0010_alter_basket_items_alter_basketitem_product'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='basket',
            name='items',
        ),
        migrations.AddField(
            model_name='basketitem',
            name='basket',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='user.basket'),
        ),
        migrations.AlterField(
            model_name='basket',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='basketitem',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='basket_items', to='shop.product'),
        ),
        migrations.AlterField(
            model_name='basketitem',
            name='quantity',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
