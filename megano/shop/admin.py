from django.contrib import admin
from django.contrib.contenttypes import admin as cadmin
from django.http import HttpRequest, HttpResponse
from django.db.models import QuerySet
from .models import Product, Order, Review, Category, Tag, Specification, Payment, OrderItem, ProductImage
from mptt.admin import MPTTModelAdmin
from django.utils.safestring import mark_safe



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
    list_display = 'id', 'user', 'created_at', 'delivery', 'payment_type', \
        'total_cost', 'status', 'city', 'address', 'full_name', 'email', 'phone'

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


class ProductImageInline(admin.TabularInline):
    model = ProductImage


class ProductTagInline(admin.StackedInline):
    model = Product.tags.through


class ProductSpecificationInline(admin.StackedInline):
    model = Product.specifications.through


class ProductReviewInLine(admin.TabularInline):
    model = Review


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    actions = [
        mark_limited,
        mark_unlimited,
    ]
    inlines = [
        ProductSpecificationInline,
        ProductTagInline,
        ProductReviewInLine,
        ProductImageInline,
    ]
    list_display = 'id', 'category', 'price', 'count', 'sold_amount', 'date', 'title', 'description',  \
       'full_description', 'limited', 'free_delivery', 'reviews', 'rating', 'slug'

    def get_queryset(self, request):
        return Product.objects.prefetch_related('specifications', 'tags')



@admin.action(description='Make Category archived')
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True)


@admin.action(description='Make Category unarchived')
def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False)




# class CategoryProductInline(admin.StackedInline):
#     model = Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    actions = [
        mark_archived,
        mark_unarchived,
    ]
    list_display = 'id', 'title', 'archived', 'slug', 'parent', 'image'

    def get_queryset(self, request):
        return Category.objects.prefetch_related('products')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = 'author', 'text', 'product', 'date', 'rate'

    def get_queryset(self, request):
        return Review.objects.select_related('author').select_related('product')




@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = 'src', 'product'

    def image_show(self, obj):
        if obj.src:
            return mark_safe("<img src='{}' width='60' />".format(obj.src))
        return "None"

    image_show.__name__ = "Картинка"




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

