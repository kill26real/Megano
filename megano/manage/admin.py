from django.contrib import admin
from .models import DeliveryType

@admin.register(DeliveryType)
class DeliveryTypeAdmin(admin.ModelAdmin):
    list_display = 'name', 'price', 'free_delivery'