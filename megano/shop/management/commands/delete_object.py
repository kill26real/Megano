from django.core.management import BaseCommand
from django.contrib.auth.models import User
from shop.models import Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('delete product')
        p = Product.objects.get(id=3)
        p.delete()
        self.stdout.write('success')
