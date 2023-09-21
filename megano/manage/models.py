from django.db import models


class DeliveryType(models.Model):

    name = models.CharField(max_length=40)
    price = models.DecimalField(default=0, max_digits=6, decimal_places=2)
    free_delivery = models.DecimalField(default=2000, max_digits=11, decimal_places=2)


    def __str__(self):
        return self.name