from django_filters.rest_framework import filters, FilterSet, Filter
from shop.models import Product


# class ProductFilter(FilterSet):
#     class Meta:
#         model = Product
#         fields = {
#             'category': ['exact'],
#             'price': ['gt', 'lt']
#         }


# class ProductFilter(Filter):
#     def filter(self, qs, value):
#         if value:
#             return qs.filter(subcategory=value)
#         else:
#             return qs.all()



# category = Category.objects.get(id=pk)
# products = Product.objects.filter(productss__in=category)



class CatalogFilter(FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')
    # category = ProductFilter(field_name="category")
    # category = filters.CharFilter(field_name='relationship__name', lookup_expr='contains')

    class Meta:
        model = Product
        fields = ['title', 'free_delivery']

    # username = filters.CharFilter()
    # login_timestamp = filters.IsoDateTimeFilter(field_name='last_login')
    #
    # class Meta:
    #     model = User
    #     fields = {
    #         'username': ['exact', 'contains'],
    #         'login_timestamp': ['exact'],
    #     }

# class CatalogsFilter(FilterSet):
#     category = ProductFilter(name="category")
#
#     class Meta:
#         model = CatalogFilter
#         fields = ['category']


