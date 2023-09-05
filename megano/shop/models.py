from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    class Meta:
        ordering = ['name', 'price']

    name = models.CharField(max_length=40)
    description = models.TextField(null=False, blank=True)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    sold_amount = models.IntegerField(default=0)
    limited = models.BooleanField(default=0)
    sort_index = models.IntegerField(default=0)


    def __str__(self):
        return self.name


class Image(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    img = models.ImageField(upload_to=f'images_products/{product.name}/')
    alt = models.CharField(null=False, blank=True, max_length=100)


class Category(models.Model):

    name = models.CharField(max_length=40)
    icon = models.ImageField(upload_to='images_categories/')
    products = models.ManyToManyField(Product, related_name='categories')
    archived = models.BooleanField(default=True)


    def __str__(self):
        return self.name


class Comment(models.Model):
    class Meta:
        ordering = ['-published_at']


    text = models.TextField(null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    published_at = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rate = models.IntegerField(default=10)


    def text_short(self):
        if len(str(self.text)) < 100:
            return self.text
        return self.text[:100] + '...'


class Order(models.Model):
    # CHOICES = (
    #     ('Visa'),
    #     ('MasterCard'),
    #     ('AmericanExpress'),
    #     ('Cash'),
    #     ('QR-Code'),
    # )


    delivery_adress = models.TextField(default='pickup')
    promocode = models.CharField(max_length=20, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    products = models.ManyToManyField(Product, related_name='orders')
    payment_method = models.CharField(max_length=40)
    paid = models.BooleanField(default=0)
