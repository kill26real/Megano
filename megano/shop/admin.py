from django.contrib import admin
from django.contrib.contenttypes import admin as cadmin
from django.http import HttpRequest, HttpResponse
from genericadmin.admin import GenericAdminModelAdmin, TabularInlineWithGeneric, StackedInlineWithGeneric
from django.db.models import QuerySet
from .models import Product, Order, Review, Category, Image, Tag, Specification, Payment, OrderItem
from mptt.admin import MPTTModelAdmin



@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = 'id', 'order', 'quantity', 'product', 'sum'

    def get_queryset(self, request):
        return OrderItem.objects.select_related('product').select_related('order')


class OrderItemInLine(admin.TabularInline):
    model = OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [
        OrderItemInLine,
    ]
    list_display = 'id', 'user', 'created_at', 'delivery_type', 'payment_type', \
        'total_cost', 'status', 'city', 'address', 'promocode'

    def get_queryset(self, request):
        return Order.objects.select_related('user')



@admin.action(description='Make Payment paid')
def mark_paid(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(paid='P')


@admin.action(description='Make Payment not paid')
def mark_unpaid(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(paid='N')

@admin.action(description='Make Payment rejected')
def mark_payment_rejected(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(paid='PR')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    actions = [
        mark_paid,
        mark_unpaid,
        mark_payment_rejected,
    ]
    list_display = 'user', 'number', 'created_at', 'code', 'paid', 'order'

    def get_queryset(self, request):
        return Payment.objects.select_related('user', 'order')




@admin.action(description='Make Product limited')
def mark_limited(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(limited=True)


@admin.action(description='Make Product unlimited')
def mark_unlimited(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(limited=False)


@admin.action(description='Make Product free dilevery')
def mark_free_delivery(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(free_delivery=True)


@admin.action(description='Unmake Product free dilevery')
def unmark_free_delivery(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(free_delivery=False)


class ImageInline(cadmin.GenericTabularInline):
    model = Image


class ProductTagInline(admin.StackedInline):
    model = Product.tags.through


class ProductSpecificationInline(admin.StackedInline):
    model = Product.specifications.through


class ProductReviewInLine(admin.TabularInline):
    model = Review


@admin.register(Product)
class ProductAdmin(GenericAdminModelAdmin):

    actions = [
        mark_limited,
        mark_unlimited,
    ]
    inlines = [
        ProductSpecificationInline,
        ProductTagInline,
        ProductReviewInLine,
        ImageInline,
    ]
    list_display = 'id', 'category', 'price', 'count', 'sold_amount', 'date', 'title', 'description',  \
       'full_description', 'limited', 'free_delivery', 'reviews', 'rating', 'slug'

    def get_queryset(self, request):
        return Product.objects.prefetch_related('images', 'specifications', 'tags')




@admin.action(description='Make Category archived')
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True)


@admin.action(description='Make Category unarchived')
def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False)




# class CategoryProductInline(admin.StackedInline):
#     model = Product


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    actions = [
        mark_archived,
        mark_unarchived,
    ]
    inlines = [
        # CategoryProductInline,
        ImageInline,
    ]
    list_display = 'id', 'title', 'archived', 'slug'

    def get_queryset(self, request):
        return Category.objects.prefetch_related('products')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = 'author', 'text', 'product', 'date', 'rate'

    def get_queryset(self, request):
        return Review.objects.select_related('author').select_related('product')




@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = 'alt', 'src'




@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = 'id', 'name'




class SpecificationProductInline(admin.TabularInline):
    model = Specification.products.through


@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    inlines = [
        SpecificationProductInline,
    ]
    list_display = 'name', 'value'

    def get_queryset(self, request):
        return Specification.objects.prefetch_related('products')

