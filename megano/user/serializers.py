from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from generic_relations.relations import GenericRelatedField
from rest_framework import serializers
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.models import BaseUserManager
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.validators import UniqueValidator
from .models import Profile, Basket, BasketItem, ProfileImage
from rest_framework.authtoken.models import Token
from phonenumber_field.serializerfields import PhoneNumberField


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['username', 'email']
#
#
# class UserLoginSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['username', 'password']
#         extra_kwargs = {
#             'password': {'write_only': True},
#         }


# class RegisterSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField(
#         required=True,
#         validators=[UniqueValidator(queryset=User.objects.all())]
#     )
#
#     password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
#     password2 = serializers.CharField(write_only=True, required=True)
#
#     class Meta:
#         model = User
#         fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')
#         extra_kwargs = {
#             'first_name': {'required': True},
#             'last_name': {'required': True},
#             'password': {'write_only': True},
#             'password2': {'write_only': True}
#         }

class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileImage
        fields = ['src', 'alt']


class ProfileSerializer(serializers.ModelSerializer):
    fullName = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['fullName', 'email', 'phone', 'avatar']

    def get_avatar(self, obj):
        try:
            ava = ProfileImage.objects.get(profile=obj)
            return ProfileImageSerializer(ava, many=False).data
        except ObjectDoesNotExist:
            return {}
    def get_fullName(self, obj):
        return obj.full_name

    def get_email(self, obj):
        return obj.user.email


# class PasswordSerializer(serializers.ModelSerializer):
#
#     old_password = serializers.CharField()
#     new_password = serializers.CharField()
#     new_password_repeat = serializers.CharField()
#
#     class Meta:
#         model = User
#         fields = ['old_password', 'new_password', 'new_password_repeat']
#
#
# class ChangeAvatarSerializer(serializers.ModelSerializer):
#     avatar = serializers.FileField()
#     alt = serializers.CharField(max_length=30)
#     class Meta:
#         model = Image
#         fields = ['avatar', 'alt']



# def save(self, **kwargs):
    #     basket_id = self.context['basket_id']
    #     product_id = self.validated_data['product_id']
    #     quantity = self.validated_data['quantity']
    #     try:
    #         basket_item = BasketItem.objects.get(product_id=product_id, basket_id=basket_id)
    #         basket_item.quantity += quantity
    #         basket_item.save()
    #         self.instance = basket_item
    #     except:
    #         self.instance = BasketItem.objects.create(basket=basket_id, **self.validated_data)
    #
    #     return self.instance