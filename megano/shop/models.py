import datetime
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MaxValueValidator, MinValueValidator
from computed_property import ComputedTextField
from manage.models import DeliveryType


# def get_storage_path(instance, filename):
#     if instance.content_type.model == 'Product':
#         product = Product.objects.get(id=instance.oject_id)
#         name_object = product.name
#         return f'/files/product/{name_object}/{filename}'
#
#     elif instance.content_type.model == 'Category':
#         category = Category.objects.get(id=instance.oject_id)
#         name_object = category.title
#         return f'/files/category/{name_object}/{filename}'
#
#     elif instance.content_type.model == 'Subcategory':
#         category = Subcategory.objects.get(id=instance.oject_id)
#         name_object = category.title
#         return f'/files/subcategory/{name_object}/{filename}'
#
#     elif instance.content_type.model == 'Profile':
#         profile = Product.objects.get(id=instance.oject_id)
#         name_object = profile.name
#         return f'/files/profile/{name_object}/{filename}'


class Image(models.Model):

    img = models.ImageField(upload_to='files/')
    alt = models.CharField(null=False, blank=True, max_length=100)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
    #     limit_choices_to={"model__in": ("Product", "Category", "Subcategory", "Profile")},
    #     related_name="votes")
    object_id = models.PositiveIntegerField()
    object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ('content_type', 'object_id')

    def __str__(self):
        return self.alt


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False, blank=True)

    def __str__(self):
        return self.name


class Specification(models.Model):

    name = models.CharField(max_length=100, null=False, blank=True)
    value = models.CharField(max_length=100, null=False, blank=True)

    def __str__(self):
        return f'name: {self.name}, value: {self.value}'


class Category(models.Model):

    class Meta:
        ordering = ['title']
        verbose_name = "category"
        verbose_name_plural = "categories"

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=40)
    icon = GenericRelation(Image, related_name='icon')
    archived = models.BooleanField(default=True)
    slug = models.SlugField(max_length=40)


    def __str__(self):
        return self.title


class Subcategory(models.Model):
    class Meta:
        ordering = ['title']
        verbose_name = "subcategory"
        verbose_name_plural = "subcategories"

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=40)
    icon = GenericRelation(Image, related_name='icon')
    archived = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    slug = models.SlugField(max_length=40)


    def __str__(self):
        return self.title



class Product(models.Model):
    class Meta:
        ordering = ['name', 'price']
        verbose_name = "product"


    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    subcategory = models.ForeignKey(Subcategory, on_delete=models.PROTECT, related_name='products')
    price = models.DecimalField(default=0, max_digits=9, decimal_places=2)
    amount = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=40)
    description = models.TextField(null=False, blank=True)
    sold_amount = models.IntegerField(default=0)
    limited = models.BooleanField(default=0)
    free_delivery = models.BooleanField(default=0)
    images = GenericRelation(Image, related_query_name='product')
    tags = models.ManyToManyField(Tag, related_query_name='products')
    specifications = models.ManyToManyField(Specification, related_name='products')
    reviews_count = models.IntegerField(default=0)
    slug = models.SlugField(max_length=40)


    def __str__(self):
        return self.name

    @property
    def product_tags(self):
        tag_list = []
        for tag in self.tags.all():
            tag_list.append(tag.name)
        return tag_list

    @property
    def rating(self):
        rat = 0
        i = 0
        reviews = self.reviews.all()
        print(reviews)
        if not reviews:
            return 5
        sums = [review.rate for review in reviews]
        for su in sums:
            i += 1
            rat += su
        total = round(rat / i, 1)
        return total




class Review(models.Model):
    class Meta:
        ordering = ['-published_at']


    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(null=False, blank=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rate = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(5)])
    published_at = models.DateTimeField(auto_now_add=True)


    def text_short(self):
        if len(str(self.text)) < 100:
            return self.text
        return self.text[:100] + '...'

    def __str__(self):
        return f'author: {self.author.username}, text: {self.text[:10]}...'



class Sale(models.Model):


    id = models.AutoField(primary_key=True)
    old_price = models.DecimalField(default=0, max_digits=9, decimal_places=2)
    new_price = models.DecimalField(default=0, max_digits=9, decimal_places=2)
    date_from = models.DateTimeField(default=datetime.datetime.now, blank=True)
    date_to = models.DateTimeField(default=datetime.datetime.now, blank=True)
    product = models.OneToOneField(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f'old: {self.old_price}, new: {self.new_price}, product:{self.product}'


class Order(models.Model):
    class Meta:
        ordering = ['-created_at']

    PAYMENT_TYPE_CHOICES = (
        ('V', 'Visa'),
        ('MC', 'MasterCard'),
        ('PP', 'PayPal'),
        ('AE', 'AmericanExpress'),
        ('E', 'Electron'),
        ('M', 'Maestro'),
        ('D', 'Delta'),
        ('C', 'Cash'),
        ('QR', 'QR-Code'),
        ('O', 'Online'),
    )

    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    delivery_type = models.ForeignKey(DeliveryType, on_delete=models.PROTECT)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    city = models.CharField(max_length=40, blank=True)
    delivery_adress = models.CharField(max_length=100, blank=True)
    promocode = models.CharField(max_length=20, null=False, blank=True)

    @property
    def delivery_price(self):
        total = 0
        items = self.items.all()
        sums = [item.sum for item in items]
        for su in sums:
            total += su
        if self.delivery_type.name == 'Express' or total < self.delivery_type.free_delivery:
            return self.delivery_type.price
        return 0

    @property
    def total_cost(self):
        total = 0
        items = self.items.all()
        sums = [item.sum for item in items]
        for su in sums:
            total += su
        return total + self.delivery_price



    @property
    def status(self):
        if self.payment:
            for pay in self.payment.all():
                if pay.paid == 'P':
                    return 'Paid'
        return 'Created'

    def __str__(self):
        return f'Order#{self.id}. user: {self.user}, cost: {self.total_cost}, date:{str(self.created_at)[:10]}'


class OrderItem(models.Model):

    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveSmallIntegerField(default=0)

    @property
    def sum(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f'{self.product.name} - {self.quantity}: {self.sum}'



class Payment(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    number = models.IntegerField(blank=False, null=True)
    created_at = models.DateTimeField(auto_now=True)
    code = models.IntegerField(blank=False, null=True)
    paid = models.BooleanField(default=0)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payment')

    def __str__(self):
        return f'Payment. User:{self.user}, sum: {self.order.total_cost}'


# class Category(MPTTModel):
#
#     class Meta:
#         ordering = ['title']
#         verbose_name = "category"
#         verbose_name_plural = "categories"
#
#     id = models.AutoField(primary_key=True)
#     title = models.CharField(max_length=40)
#     icon = GenericRelation(Image)
#     products = models.ManyToManyField(Product, related_name='categories')
#     parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
#     archived = models.BooleanField(default=True)
#     slug = models.SlugField(max_length=40)
#
#
#     def __str__(self):
#         return self.title

