from django.db import models


class Catalog(models.Model):
    wb_id = models.PositiveIntegerField(blank=False, unique=True)
    name = models.CharField(max_length=200, null=False, unique=True)
    shard = models.CharField(max_length=100, null=False)
    query = models.CharField(max_length=100, null=False)
    active = models.BooleanField(default=False)
    low_price = models.PositiveIntegerField(blank=True)
    high_price = models.PositiveIntegerField(blank=True)
    parent_id = models.PositiveIntegerField(blank=True)
    delta = models.PositiveSmallIntegerField(blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    wb_id = models.PositiveIntegerField(blank=False, unique=True)
    name = models.CharField(max_length=200, null=False)
    catalog = models.ForeignKey(Catalog, related_name='goods',
                                on_delete=models.CASCADE, blank=False)

    def __str__(self):
        return self.name


class Price(models.Model):
    product = models.ForeignKey(Product, related_name='prices',
                                on_delete=models.CASCADE, blank=False)
    upload_date = models.DateTimeField()
    price = models.PositiveIntegerField(blank=False)
