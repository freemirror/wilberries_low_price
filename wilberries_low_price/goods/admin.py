from django.contrib import admin
from goods.models import Product, Price, Catalog


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ('product', 'upload_date', 'price')


@admin.register(Catalog)
class CatalogAdmin(admin.ModelAdmin):
    list_display = ('wb_id', 'name', 'shard', 'query', 'active', 'low_price',
                    'high_price', 'parent_id', 'delta')


class ProductPriceInLine(admin.TabularInline):
    model = Price
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('wb_id', 'name', 'catalog')
    inlines = (ProductPriceInLine,)
