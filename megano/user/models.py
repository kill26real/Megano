from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User
from shop.models import Order, Product, Category, Image
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import RegexValidator


class Profile(models.Model):
    class Meta:
        verbose_name = "profile"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = GenericRelation(Image, related_name='profile')
    phone = models.CharField(validators=[RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. "
                "Up to 15 digits allowed.")], max_length=16, blank=True, null=False)


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
