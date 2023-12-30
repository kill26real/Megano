from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from .models import Product, Tag, Category, Order, Specification, Review, OrderItem, Payment, ProductImage
from django.contrib.auth.models import User
from user.models import Profile
from manage.models import DeliveryType
from user.models import BasketItem
from datetime import datetime, timezone


class ChoicesField(serializers.Field):
    def __init__(self, choices, **kwargs):
        self._choices = dict(choices)
        super(ChoicesField, self).__init__(**kwargs)

    def to_representation(self, obj):
        for choice in self._choices.values():
            if obj == choice:
                return obj
        return self._choices[obj]

    def to_internal_value(self, data):
        return getattr(self._choices, data)



# class ImageSerializer(serializers.ModelSerializer):
#     # img = serializers.ImageField(max_length=None, use_url=True, allow_null=False, required=True)
#
#     class Meta:
#         model = Image
#         fields = ['src', 'alt']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'image']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['alt', 'src']


class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'title', 'subcategories', 'image']

    def get_subcategories(self, obj):
        queryset = Category.objects.filter(parent=obj.id)
        return [SubcategorySerializer(q).data for q in queryset]


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['author', 'email', 'text', 'rate', 'date']


    def get_author(self, obj):
        return obj.author.username

    def get_email(self, obj):
        return obj.author.email


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ['name', 'value']


class ProductSerializer(serializers.ModelSerializer):
    reviews = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    specifications = SpecificationSerializer(many=True, read_only=True)
    date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    tags = TagSerializer(read_only=True, many=True)
    class Meta:
        model = Product
        fields = ['id', 'category', 'price', 'count', 'date', 'title', 'description', 'full_description',
                  'free_delivery', 'tags', 'images', 'reviews', 'specifications', 'rating']

    def get_reviews(self, obj):
        queryset = Review.objects.filter(product=obj)
        return [ReviewSerializer(q).data for q in queryset]


    def get_images(self, obj):
        return [ProductImageSerializer(img).data for img in ProductImage.objects.filter(product=obj)]


    def get_category(self, obj):
        return obj.category.id

    def get_price(self, obj):
        if obj.sale_price != 0 and datetime.now(timezone.utc) < obj.date_to and datetime.now(timezone.utc) > obj.date_from:
            return float(obj.sale_price)
        else:
            return float(obj.price)


class ProductShortSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    category = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['id', 'category', 'price', 'count', 'date', 'title',
                  'description', 'free_delivery', 'tags', 'images', 'reviews', 'rating']

    def get_category(self, obj):
        return obj.category.id

    def get_price(self, obj):
        if obj.sale_price != 0 and datetime.now(timezone.utc) < obj.date_to and datetime.now(timezone.utc) > obj.date_from:
            return float(obj.sale_price)
        else:
            return float(obj.price)

    def get_images(self, obj):
        return [ProductImageSerializer(img).data for img in ProductImage.objects.filter(product=obj)]


class ProductShortBasketSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    category = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['id', 'category', 'price', 'count', 'date', 'title',
                  'description', 'free_delivery', 'tags', 'images', 'reviews', 'rating']

    def get_category(self, obj):
        return obj.category.id

    def get_price(self, obj):
        if obj.sale_price != 0 and datetime.now(timezone.utc) < obj.date_to and datetime.now(timezone.utc) > obj.date_from:
            return float(obj.sale_price)
        else:
            return float(obj.price)

    def get_images(self, obj):
        return [ProductImageSerializer(img).data for img in ProductImage.objects.filter(product=obj)]

    def get_count(self, obj):
        basket = self.context["basket"]
        item = BasketItem.objects.get(product=obj, basket=basket)
        return item.quantity


class ProductShortOrderSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    category = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()
    shortDescription = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['id', 'category', 'price', 'count', 'date', 'title',
                  'description', 'shortDescription', 'free_delivery', 'tags', 'images', 'reviews', 'rating']

    def get_category(self, obj):
        return obj.category.id

    def get_description(self, obj):
        return obj.full_description

    def get_shortDescription(self, obj):
        return obj.description

    def get_images(self, obj):
        return [ProductImageSerializer(img).data for img in ProductImage.objects.filter(product=obj)]

    def get_price(self, obj):
        if obj.sale_price != 0 and datetime.now(timezone.utc) < obj.date_to and datetime.now(timezone.utc) > obj.date_from:
            return float(obj.sale_price)
        else:
            return float(obj.price)

    def get_count(self, obj):
        order = self.context["order"]
        item = OrderItem.objects.get(product=obj, order=order)
        return item.quantity


class OrderSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    createdAt = serializers.SerializerMethodField()
    fullName = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    deliveryType = serializers.SerializerMethodField()
    paymentType = serializers.SerializerMethodField()
    orderId = serializers.SerializerMethodField()
    totalCost = serializers.SerializerMethodField()
    paymentError = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'createdAt', 'fullName', 'email', 'phone', 'deliveryType', 'paymentType', 'total_cost',
                  'status', 'city', 'address', 'products', 'orderId', 'totalCost', 'paymentError']


    def get_deliveryType(self, obj):
        if obj.delivery.name == 'Reguar' and obj.total_cost > obj.delivery.price:
            return 'free'
        else:
            return obj.delivery.name

    def get_paymentError(self, obj):
        return obj.payment_error

    def get_totalCost(self, obj):
        return float(obj.total_cost)

    def get_orderId(self, obj):
        return obj.id

    def get_paymentType(self, obj):
        return obj.payment_type

    def get_fullName(self, obj):
        return obj.full_name

    def get_email(self, obj):
        return obj.email

    def get_phone(self, obj):
        return obj.phone

    def get_createdAt(self, obj):
        return str(obj.created_at)[:16]


    def get_products(self, obj):
        queryset = OrderItem.objects.filter(order=obj)
        return [ProductShortOrderSerializer(q.product, context={'order': obj}).data for q in queryset]


class SaleSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    sale_price = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    date_from = serializers.SerializerMethodField()
    date_to = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()


    class Meta:
        model = Product
        fields = ['id', 'price', 'sale_price', 'date_from', 'date_to', 'title', 'images']

    def get_images(self, obj):
        return [ProductImageSerializer(img).data for img in ProductImage.objects.filter(product=obj)]

    def get_price(self, obj):
        return float(obj.price)

    def get_sale_price(self, obj):
        return float(obj.sale_price)

    def get_id(self, obj):
        return str(obj.id)

    def get_date_from(self, obj):
        return str(obj.date_from)[:10]

    def get_date_to(self, obj):
        return str(obj.date_to)[:10]


# class PaymentSerializer(serializers.ModelSerializer):
#     created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
#     class Meta:
#         model = Payment
#         fields = ['number', 'code', 'order', 'created_at', 'paid']

