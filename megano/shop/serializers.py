from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from .models import Product, Image, Tag, Category, Order, Specification, Sale, Subcategory, Review, OrderItem, Payment
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
    img = serializers.ImageField(max_length=None, use_url=True, allow_null=False, required=True)

    class Meta:
        model = Image
        fields = ['img', 'alt']


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


class SubcategorySerializer(serializers.ModelSerializer):
    icon = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = Subcategory
        fields = ['id', 'title', 'icon']


class CategorySerializer(serializers.ModelSerializer):
    icon = ImageSerializer(many=True, read_only=True)
    subcategories = SubcategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'title', 'icon', 'subcategories']


class ReviewSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['author', 'text', 'rate', 'published_at']


class ProductSubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ['id']


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
    product_tags = serializers.ReadOnlyField()
    specifications = SpecificationSerializer(many=True, read_only=True)
    product_category = serializers.ReadOnlyField()
    product_subcategory = serializers.ReadOnlyField()

    # category = ProductCategorySerializer(read_only=True)
    # subcategory = ProductSubcategorySerializer(read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'product_category', 'product_subcategory', 'amount', 'created_at',
                  'description', 'free_delivery', 'images', 'product_tags', 'reviews', 'specifications', 'rating']

    def get_reviews(self, obj):
        queryset = Review.objects.filter(product=obj)
        return [ReviewSerializer(q).data for q in queryset]


class ProductShortSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    product_tags = serializers.ReadOnlyField()
    product_category = serializers.ReadOnlyField()
    product_subcategory = serializers.ReadOnlyField()

    # category = ProductCategorySerializer(read_only=True)
    # subcategory = ProductSubcategorySerializer(read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'product_category', 'product_subcategory', 'amount', 'created_at',
                  'description',
                  'free_delivery', 'images', 'product_tags', 'reviews_count', 'rating']


class SaleProductSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['name', 'images']


class SaleSerializer(serializers.ModelSerializer):
    product = SaleProductSerializer(read_only=True)

    class Meta:
        model = Sale
        fields = ['id', 'old_price', 'new_price', 'date_from', 'date_to', 'product']


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
                  'delivery_price', 'promocode', 'status', 'city', 'delivery_adress', 'items']

    def get_items(self, obj):
        queryset = OrderItem.objects.filter(order=obj)
        return [OrderItemSerializer(q).data for q in queryset]


class CreateOrderSerializer(serializers.ModelSerializer):
    city = serializers.CharField(max_length=40)
    delivery_adress = serializers.CharField(max_length=100)
    promocode = serializers.CharField(max_length=20)
    payment_type = serializers.ChoiceField(choices=Order.PAYMENT_TYPE_CHOICES)
    delivery_type = serializers.ChoiceField(choices=[type.name for type in DeliveryType.objects.all()])

    for product in Product.objects.all():
        product_name_underline = product.name.replace(" ", "_")

        exec(f"{product_name_underline} = serializers.IntegerField(default=0)")

    class Meta:
        model = Order
        exclude = ['user']


class AddOrderItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True, many=True)

    def get_product(self, obj):
        # queryset = Product.objects.filter(order_items=obj)
        queryset = Product.objects.all()
        return [q.name for q in queryset]
        # return [ProductShortSerializer(q).data for q in queryset]


    class Meta:
        model = OrderItem
        fields = ["product", "product_id", "quantity"]

class UpdateOrderSerializer(serializers.ModelSerializer):
    city = serializers.CharField(max_length=40)
    delivery_adress = serializers.CharField(max_length=100)
    promocode = serializers.CharField(max_length=20)
    payment_type = serializers.ChoiceField(choices=Order.PAYMENT_TYPE_CHOICES)
    delivery_type = serializers.ChoiceField(choices=[type.name for type in DeliveryType.objects.all()])
    product = serializers.ChoiceField(choices=[f'{prod.name}, id:{prod.id}' for prod in Product.objects.all().order_by('name')], default=0)
    quantity = serializers.IntegerField(default=0)


    class Meta:
        model = Order
        exclude = ['user']


class DeleteOrderItemSerializer(serializers.ModelSerializer):
    product = ProductShortSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True, many=True)

    class Meta:
        model = OrderItem
        fields = ["product", "product_id", "quantity"]



class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['number', 'code', 'order']

