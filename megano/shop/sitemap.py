from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Product


class ShopSitemap(Sitemap):
    changefreq = 'never'
    priority = 0.5

    def items(self):
        return Product.objects.filter(count__isnull=False)

    def lastmod(self, obj: Product):
        return obj.date