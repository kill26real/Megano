from django.contrib import admin
from django.http import HttpRequest, HttpResponse
from django.db.models import QuerySet
from .models import Product, Order, Comment, Category, Image




class OrderProductInline(admin.StackedInline):
    model = Order.products.through


@admin.action(description='Make Order paid')
def mark_paid(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(paid=True)


@admin.action(description='Make Order not paid')
def mark_unpaid(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(paid=False)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [
        OrderProductInline,
    ]
    actions = [
        mark_paid,
        mark_unpaid,
    ]
    list_display = 'pk', 'promocode', 'delivery_adress', 'created_at', 'user', 'payment_method', 'paid'

    def get_queryset(self, request):
        return Order.objects.select_related('user').prefetch_related('products')


@admin.action(description='Make Product limited')
def mark_limited(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(limited=True)


@admin.action(description='Make Product unlimited')
def mark_unlimited(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(limited=False)


class ProductCategoryInline(admin.StackedInline):
    model = Product.categories.through


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    actions = [
        mark_limited,
        mark_unlimited,
    ]
    inlines = [
        ProductCategoryInline,
    ]
    list_display = 'pk', 'name', 'description', 'price', 'sold_amount', 'limited', 'sort_index'


class CategoryProductInline(admin.StackedInline):
    model = Category.products.through


@admin.action(description='Make Category archived')
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True)


@admin.action(description='Make Category unarchived')
def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    actions = [
        mark_archived,
        mark_unarchived,
    ]
    inlines = [
        CategoryProductInline,
    ]
    list_display = 'name', 'icon', 'archived'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = 'text', 'user', 'product', 'published_at', 'rate'


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = 'product', 'img'
