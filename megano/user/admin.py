from django.contrib import admin
from .models import Profile, Basket, BasketItem, ProfileImage
from shop.models import Order, Product, Category
from django.contrib.contenttypes import admin as cadmin
from django.http import HttpRequest, HttpResponse
from django.db.models import QuerySet
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

@admin.register(ProfileImage)
class ProfileImageAdmin(admin.ModelAdmin):
    list_display = 'src', 'profile'

class ProfileImageInline(admin.TabularInline):
    model = ProfileImage


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = 'user', 'phone', 'full_name'
    inlines = [
        ProfileImageInline,
    ]

    def get_queryset(self, request):
        return Profile.objects.select_related('user')


@admin.register(BasketItem)
class BasketItemAdmin(admin.ModelAdmin):
    list_display = 'quantity', 'product', 'basket', 'sum'

    def get_queryset(self, request):
        return BasketItem.objects.select_related('product', 'basket')


class BasketItemInLine(admin.TabularInline):
    model = BasketItem


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    inlines = [
        BasketItemInLine,
    ]
    list_display = 'user', 'total_sum'

    def get_queryset(self, request):
        return Basket.objects.select_related('user')

