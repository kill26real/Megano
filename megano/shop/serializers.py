from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from .models import Product, Image, Tag, Category, Order, Specification, Review, OrderItem, Payment
from django.contrib.auth.models import User
from user.models import Profile
from manage.models import DeliveryType


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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']


class ImageSerializer(serializers.ModelSerializer):
    src = serializers.ImageField(max_length=None, use_url=True, allow_null=False, required=True)

    class Meta:
        model = Image
        fields = ['src', 'alt']


class ProfileSerializer(serializers.ModelSerializer):
    avatar = ImageSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ['user', 'phone', 'avatar']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class CategorySerializer(serializers.ModelSerializer):
    image = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'title', 'image', 'parent']


class ReviewSerializer(serializers.ModelSerializer):
    # author = UserSerializer(read_only=True)
    author = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['author', 'email', 'text', 'rate', 'date']


    def get_author(self, obj):
        return obj.author.username

    def get_email(self, obj):
        return obj.author.email


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id']


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ['name', 'value']


class ProductSerializer(serializers.ModelSerializer):
    reviews = serializers.SerializerMethodField()
    images = ImageSerializer(many=True, read_only=True)
    # product_tags = serializers.ReadOnlyField()
    specifications = SpecificationSerializer(many=True, read_only=True)
    date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    tags = TagSerializer(read_only=True, many=True)
    # product_category = serializers.ReadOnlyField()
    # category = ProductCategorySerializer(read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'category', 'price', 'count', 'date', 'title', 'description', 'full_description',
                  'free_delivery', 'images', 'tags', 'reviews', 'specifications', 'rating']

    def get_reviews(self, obj):
        queryset = Review.objects.filter(product=obj)
        return [ReviewSerializer(q).data for q in queryset]


    def get_category(self, obj):
        return obj.category.id


class ProductShortSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    category = serializers.SerializerMethodField()
    # product_category = serializers.ReadOnlyField()
    # category = ProductCategorySerializer(read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'category', 'price', 'count', 'date', 'title',
                  'description', 'free_delivery', 'images', 'tags', 'reviews', 'rating']

    def get_category(self, obj):
        return obj.category.id


class SaleSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)


    class Meta:
        model = Product
        fields = ['id', 'price', 'sale_price', 'date_from', 'date_to', 'title', 'images']


    # def get_images(self, obj):
    #     queryset = obj.images.all()
    #     return [ImageSerializer(q).data for q in queryset]



class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductShortSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'sum']


class DeliveryTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryType
        fields = ['name', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    # payment_type = serializers.ChoiceField(choices=Order.PAYMENT_TYPE_CHOICES)
    payment_type = ChoicesField(choices=Order.PAYMENT_TYPE_CHOICES)
    delivery = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    phone = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = ['id', 'created_at', 'username', 'email', 'phone', 'delivery', 'payment_type', 'total_cost',
                  'delivery_price', 'promocode', 'status', 'city', 'address', 'items']

    def get_items(self, obj):
        queryset = OrderItem.objects.filter(order=obj)
        return [OrderItemSerializer(q).data for q in queryset]


class CreateOrderSerializer(serializers.ModelSerializer):
    city = serializers.CharField(max_length=40)
    address = serializers.CharField(max_length=100)
    promocode = serializers.CharField(max_length=20)
    payment_type = serializers.ChoiceField(choices=Order.PAYMENT_TYPE_CHOICES)
    delivery_type = serializers.ChoiceField(choices=[type.name for type in DeliveryType.objects.all()])

    # for product in Product.objects.all():
    #     product_title_underline = product.title.replace(" ", "_")
    #
    #     exec(f"{product_title_underline} = serializers.IntegerField(default=0)")

    class Meta:
        model = Order
        exclude = ['user']


class UpdateOrderSerializer(serializers.ModelSerializer):
    city = serializers.CharField(max_length=40)
    address = serializers.CharField(max_length=100)
    promocode = serializers.CharField(max_length=20)
    payment_type = serializers.ChoiceField(choices=Order.PAYMENT_TYPE_CHOICES)
    delivery_type = serializers.ChoiceField(choices=[type.name for type in DeliveryType.objects.all()])
    # add_product = serializers.ChoiceField(choices=[f'{prod.title}, id:{prod.id}' for prod in Product.objects.all().order_by('title')], default=0)
    quantity_of_product_to_add = serializers.IntegerField(default=0)
    # delete_product = serializers.ChoiceField(choices=[f'{prod.title}, id:{prod.id}' for prod in Product.objects.all().order_by('title')], default=0)
    quantity_of_product_to_delete = serializers.IntegerField(default=0)



    class Meta:
        model = Order
        exclude = ['user']




class CreatePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['number', 'code', 'order']


class PaymentSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    class Meta:
        model = Payment
        fields = ['number', 'code', 'order', 'created_at', 'paid']

