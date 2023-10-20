from django_filters.rest_framework import filters, FilterSet
from shop.models import Product


# class ProductFilter(FilterSet):
#     class Meta:
#         model = Product
#         fields = {
#             'category': ['exact'],
#             'price': ['gt', 'lt']
#         }


class CatalogFilter(FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['title', 'free_delivery']