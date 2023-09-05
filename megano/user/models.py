from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User
from shop.models import Order, Product, Category

class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=False)
    surname = models.CharField(max_length=100, blank=False)
    city = models.CharField(max_length=40, blank=True)
    avatar = models.ImageField(upload_to='images_avatars/')
    date_of_birth = models.DateField(null=False, blank=True)
    e_mail = models.EmailField(max_length=100, unique=True)
    phone_number = PhoneNumberField(null=False, blank=False, unique=True)
    orders = models.ForeignKey(Order, on_delete=models.PROTECT)
    favourite_categories = models.ForeignKey(Category, on_delete=models.PROTECT)


class Cart(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, related_name='carts')
    total_sum = models.DecimalField(default=0, max_digits=8, decimal_places=2)
