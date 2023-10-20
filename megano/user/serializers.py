from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from generic_relations.relations import GenericRelatedField
from rest_framework import serializers
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.models import BaseUserManager
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.validators import UniqueValidator
from shop.models import Product, Image, Tag, Category, Order, Specification, Sale, Subcategory, Review
from shop.serializers import ProductShortSerializer
from django.contrib.auth.models import User
from .models import Profile, Basket, BasketItem
from rest_framework.authtoken.models import Token
from phonenumber_field.serializerfields import PhoneNumberField


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }


class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff')
        read_only_fields = ('id', 'is_active', 'is_staff')


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {'write_only': True},
            'password2': {'write_only': True}
        }

    # def validate(self, attrs):
    #     if attrs['password'] != attrs['password2']:
    #         raise serializers.ValidationError({"password": "Password fields didn't match."})
    #
    #     return attrs
    #
    # def create(self, validated_data):
    #     user = User.objects.create(
    #         username=validated_data['username'],
    #         email=validated_data['email'],
    #         first_name=validated_data['first_name'],
    #         last_name=validated_data['last_name']
    #     )
    #
    #     user.set_password(validated_data['password'])
    #     user.save()
    #
    #     return user


class ImageSerializer(serializers.ModelSerializer):
    src = serializers.ImageField(max_length=None, use_url=True, allow_null=False, required=True)
    alt = serializers.CharField(max_length=40, default='avatar')
    class Meta:
        model = Image
        # fields = '__all__'
        fields = ['src', 'alt']



class ProfileSerializer(serializers.ModelSerializer):
    avatar = ImageSerializer(many=True)
    user = UserSerializer(read_only=True)
    class Meta:
        model = Profile
        fields = ['user', 'phone', 'avatar']


class CreateProfileSerializer(serializers.ModelSerializer):
    # avatar = ImageSerializer(many=True)
    # avatar = ImageRelatedField(many=True, queryset=Image.objects.all())
    avatar = serializers.FileField()
    alt = serializers.CharField(max_length=30)
    phone = PhoneNumberField()
    class Meta:
        model = Profile
        fields = ['phone', 'avatar', 'alt']


class PasswordSerializer(serializers.ModelSerializer):

    old_password = serializers.CharField()
    new_password = serializers.CharField()
    new_password_repeat = serializers.CharField()

    class Meta:
        model = User
        fields = ['old_password', 'new_password', 'new_password_repeat']


class ChangeAvatarSerializer(serializers.ModelSerializer):
    avatar = serializers.FileField()
    alt = serializers.CharField(max_length=30)
    class Meta:
        model = Image
        fields = ['avatar', 'alt']


class BasketItemSerializer(serializers.ModelSerializer):
    product = ProductShortSerializer(read_only=True)

    def save(self, **kwargs):
        basket_id = self.context['basket_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        try:
            basket_item = BasketItem.objects.get(product_id=product_id, basket_id=basket_id)
            basket_item.quantity += quantity
            basket_item.save()
            self.instance = basket_item
        except:
            self.instance = BasketItem.objects.create(basket=basket_id, **self.validated_data)

        return self.instance

    class Meta:
        model = BasketItem
        fields = ['product', 'quantity', 'sum']


class AddBasketItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True, many=True)


    def get_product(self, obj):
        queryset = Product.objects.filter(items=obj)
        return [ProductShortSerializer(q).data for q in queryset]


    class Meta:
        model = BasketItem
        fields = ["product", "product_id", "quantity"]


class DeleteBasketItemSerializer(serializers.ModelSerializer):
    product = ProductShortSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True, many=True)

    class Meta:
        model = BasketItem
        fields = ["product", "product_id", "quantity"]


class BasketSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    total_sum = serializers.SerializerMethodField(method_name='main_total')

    class Meta:
        model = Basket
        fields = ['items', 'total_sum']
        read_only_fields = ['total_sum']

    def get_items(self, obj):
        queryset = BasketItem.objects.filter(basket=obj)
        return [BasketItemSerializer(q).data for q in queryset]


    def main_total(self, basket: Basket):
        items = basket.items.all()
        total = sum([item.quantity * item.product.price for item in items])
        return total

