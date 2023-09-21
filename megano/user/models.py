from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User
from shop.models import Order, Product, Category, Image
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from computed_property import ComputedTextField


class Profile(models.Model):
    class Meta:
        verbose_name = "profile"

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = GenericRelation(Image, related_name='profile')
    phone = PhoneNumberField(null=False, blank=False, unique=True)



class Basket(models.Model):

    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_query_name='basket')

    @property
    def total_sum(self):
        total = 0
        items = self.items.all()
        sums = [item.sum for item in items]
        for su in sums:
            total += su
        return total

    def __str__(self):
        return f'Basket. User:{self.user}, sum: {self.total_sum}'


class BasketItem(models.Model):

    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name="items", null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='basket_items')
    quantity = models.PositiveSmallIntegerField(default=0)

    @property
    def sum(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f'{self.product.name} - {self.quantity}: {self.sum}'

