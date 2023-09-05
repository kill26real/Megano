from django.urls import path
from django.views.generic import TemplateView
from .views import (
    ProductsIndexView,
    ProductsListView,
    ProductsDetailsView,
)

app_name = 'shop'

urlpatterns = [
    path('', ProductsIndexView.as_view(), name="index"),
    # path('', TemplateView.as_view(template_name="shop/index.html")),
    path('about', TemplateView.as_view(template_name="shop/about.html")),
    path('catalog/', ProductsListView.as_view(), name="catalog"),
    path('catalog/<int:pk>/', TemplateView.as_view(template_name="shop/catalog.html")),
    path('sale/', TemplateView.as_view(template_name="shop/sale.html")),
    path('product/<int:pk>/', ProductsDetailsView.as_view(), name="product-details"),
]

