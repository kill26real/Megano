from django.urls import path
from django.views.generic import TemplateView
from .views import (
    ProfileView, register_view, ProfileUpdateView, MyLoginView, MyLogoutView,
)

app_name = 'user'

urlpatterns = [
    path('account/', TemplateView.as_view(template_name="user/account.html")),
    path('cart/', TemplateView.as_view(template_name="user/cart.html")),
    path('payment/<int:id>/', TemplateView.as_view(template_name="user/payment.html")),
    path('logout/', MyLogoutView.as_view(), name='logout'),
    path('payment-someone/', TemplateView.as_view(template_name="user/paymentsomeone.html")),
    path('<int:pk>/', ProfileView.as_view(), name="profile"),
    path('progress-payment/', TemplateView.as_view(template_name="user/progressPayment.html")),
    path('sign-in/', MyLoginView.as_view(), name="sign-in"),
    path('sign-up/', register_view, name="sign-up"),
    path('history-order/', TemplateView.as_view(template_name="user/historyorder.html")),
    path('order-detail/<int:id>/', TemplateView.as_view(template_name="user/oneorder.html")),
    path('orders/<int:id>/', TemplateView.as_view(template_name="user/order.html")),
]