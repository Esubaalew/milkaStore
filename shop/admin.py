from django.contrib import admin
from .models import Order, Product


class OrderAdmin(admin.ModelAdmin):
    model = Order
    list_display = ('product_name', 'full_name', 'address', 'phone_number', 'comment', 'quantity', 'order_date')
    list_filter = ('product', 'full_name', 'address', 'phone_number', 'comment', 'quantity', 'order_date')
    search_fields = ('product__name', 'full_name', 'address', 'phone_number', 'comment', 'quantity', 'order_date')
    ordering = ('-order_date',)

    def product_name(self, obj):
        return obj.product.name
    product_name.short_description = 'Product'


class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ('name', 'short_description', 'image', 'price', 'date_added')
    list_filter = ('name', 'price', 'date_added')
    search_fields = ('name', 'price', 'date_added')
    ordering = ('-date_added',)

    def short_description(self, obj):
        return obj.description if len(obj.description) <= 50 else f"{obj.description[:50]}..."
    short_description.short_description = 'Description'


admin.site.register(Order, OrderAdmin)
admin.site.register(Product, ProductAdmin)


# Change the title and header of the admin site
admin.site.site_header = "Store Administration"
admin.site.site_title = "Shop Admin Portal"
admin.site.index_title = "Welcome to the Shop Admin Dashboard"
