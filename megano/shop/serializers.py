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
        # print(obj)
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
    category = ProductCategorySerializer(read_only=True)
    subcategory = ProductSubcategorySerializer(read_only=True)
    # rating = serializers.IntegerField(read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'category', 'subcategory', 'amount', 'created_at', 'description',
                  'free_delivery', 'images', 'product_tags', 'reviews', 'specifications', 'rating']

    def get_reviews(self, obj):
        queryset = Review.objects.filter(product=obj)
        return [ReviewSerializer(q).data for q in queryset]


class ProductShortSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    category = ProductCategorySerializer(read_only=True)
    subcategory = ProductSubcategorySerializer(read_only=True)
    # rating = serializers.IntegerField(read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'category', 'subcategory', 'amount', 'created_at', 'description',
                  'free_delivery', 'images', 'tags', 'reviews_count', 'rating']



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
    # total_cost = serializers.SerializerMethodField(method_name='main_total')
    user = UserSerializer(read_only=True)
    payment_type = ChoicesField(choices=Order.PAYMENT_TYPE_CHOICES)
    delivery_type = DeliveryTypeSerializer()
    class Meta:
        model = Order
        fields = ['id', 'created_at', 'user', 'delivery_type', 'payment_type', 'total_cost', 'delivery_price', 'status', 'city',
                  'delivery_adress', 'items']

    def get_items(self, obj):
        queryset = OrderItem.objects.filter(order=obj)
        return [OrderItemSerializer(q).data for q in queryset]


    # def main_total(self, order: Order):
    #     items = order.items.all()
    #     total = sum([item.quantity * item.product.price for item in items])
    #     return total



# class AddOrderItemSerializer(serializers.ModelSerializer):
#     product = serializers.SerializerMethodField()
#     product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True, many=True)
#
#     def get_product(self, obj):
#         queryset = Product.objects.filter(items=obj)
#         # queryset = Product.objects.all()
#         return [ProductShortSerializer(q).data for q in queryset]
#
#     def save(self, **kwargs):
#         order_id = self.context['order_id']
#         product_id = self.validated_data['product_id']
#         quantity = self.validated_data['quantity']
#         try:
#             order_item = OrderItem.objects.get(product=product_id, order=order_id)
#             order_item.quantity += quantity
#             order_item.save()
#             self.instance = order_item
#         except:
#             self.instance = OrderItem.objects.create(order=order_id, **self.validated_data)
#
#         return self.instance
#
#     class Meta:
#         model = OrderItem
#         fields = ["product", "product_id", "quantity"]


class DeliveryTypeCreateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryType
        fields = ['name']


class CreateOrderSerializer(serializers.ModelSerializer):
    # items = AddOrderItemSerializer(many=True)
    # total_cost = serializers.SerializerMethodField(method_name='main_total')
    city = serializers.CharField(max_length=40)
    delivery_adress = serializers.CharField(max_length=100)
    promocode = serializers.CharField(max_length=20)
    payment_type = serializers.ChoiceField(choices=Order.PAYMENT_TYPE_CHOICES)
    delivery_type = DeliveryTypeCreateOrderSerializer(many=True, read_only=True)


    for product in Product.objects.all():
        product_name_underline = product.name.replace(" ", "_")

        exec(f"{product_name_underline} = serializers.IntegerField(default=0)")


    class Meta:
        model = Order
        # fields = '__all__'
        exclude = ['user']
        # fields = ['city', 'delivery_adress', 'promocode', 'delivery_type', 'payment_type']

    # items_dict = {}
    # fieldss = []
    #
    # products = Product.objects.all()
    # for product in products:
    #     # productid = product.id
    #     items_dict['product'] = product.name
    #     items_dict['product_id'] = product.id
    #     items_dict['quantity'] = 0
    #
    #     exec(f"item{product.id} = AddOrderItemSerializer(items_dict)")
    #     fieldss.append(f"item{product.id}")


    # def get_field_names(self, declared_fields, info):
    #     # global fieldss
    #     expanded_fields = super(CreateOrderSerializer, self).get_field_names(declared_fields, info)
    #     return expanded_fields + self.fieldss


    # def get_items(self, obj):
    #     queryset = OrderItem.objects.filter(order=obj)
    #     return [AddOrderItemSerializer(q).data for q in queryset]


    # def main_total(self, order: Order):
    #     items = order.items.all()
    #     total = sum([item.quantity * item.product.price for item in items])
    #     return total



class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['number', 'code', 'order']




# def create(self, validated_data):
#     sum = 0
#     products = validated_data.pop('products_id')
#     for prod in products:
#         sum += prod.price
#     validated_data['total_sum'] = sum
#     # validated_data['user'] = self.context['request'].user
#     basket = Basket.objects.create(**validated_data)
#     basket.products.add(*products)
#     # for prod in products:
#     #     basket.products.add(prod)
#     return basket
