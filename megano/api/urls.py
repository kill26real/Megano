from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework import routers
from rest_framework_nested import routers as rt

from .views import (
    LogoutView,
    MyLoginView,
    RegisterView,
    CategoryList,
    CatalogView,
    ProductsPopularCatalogList,
    ProductsLimitedCatalogList,
    SalesList,
    BannersList,
    BasketDetail,
    OrdersList,
    OrderDetailsView,
    PaymentView,
    ProfileDetail,
    ChangePassword,
    UpdateProfileAvatar,
    ProductDetailsView,
    ReviewView,
    TagListView,
)

app_name = 'api'

urlpatterns = [
    path('', include('rest_framework.urls')),
    path('sign-in', MyLoginView.as_view(), name='sign-in'),
    path('sign-up', RegisterView.as_view(), name='sign-up'),
    path('sign-out', LogoutView.as_view(), name='sign-out'),
    path('categories/', CategoryList.as_view(), name='categories-list'),
    path('catalog/', CatalogView.as_view(), name="catalog"),
    path('products/popular/', ProductsPopularCatalogList.as_view(), name="popular"),
    path('products/limited/', ProductsLimitedCatalogList.as_view(), name="limited"),
    path('sales/', SalesList.as_view(), name="sales"),
    path('banners/', BannersList.as_view(), name="banners"),
    path('basket', BasketDetail.as_view(), name="basket"),
    path('orders', OrdersList.as_view(), name="orders"),
    path('order/<int:pk>', OrderDetailsView.as_view(), name="order-details"),
    path('payment/<int:pk>', PaymentView.as_view(), name="payment"),
    path('profile', ProfileDetail.as_view(), name="profile"),
    path('profile/password', ChangePassword.as_view(), name="change-password"),
    path('profile/avatar', UpdateProfileAvatar.as_view(), name="avatar"),
    path('tags', TagListView.as_view(), name="tags"),
    path('product/<int:pk>', ProductDetailsView.as_view(), name="product"),
    path('product/<int:pk>/reviews', ReviewView.as_view(), name="review")
]