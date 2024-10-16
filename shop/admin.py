from django.contrib import admin
from unfold.admin import ModelAdmin
from django.utils.html import format_html
from .models import Order, Product, Category, Subcategory, Brand, ProductModel, Stock
from django.core.exceptions import ValidationError
from django.http import HttpResponse
import csv

class OrderAdmin(ModelAdmin):
    model = Order
    list_display = (
        'product_name',
        'full_name',
        'address',
        'phone_number',
        'comment',
        'quantity',
        'order_date',
        'is_paid',
    )
    list_filter = (
        'product',
        'full_name',
        'address',
        'phone_number',
        'quantity',
        'order_date',
        'is_paid',
    )
    search_fields = (
        'product__name',
        'full_name',
        'address',
        'phone_number',
        'comment'
    )
    ordering = ('-order_date',)

    def product_name(self, obj):
        return obj.product.name
    product_name.short_description = 'Product'

    def export_as_csv(self, request, queryset):
        # Create the response object for CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders.csv"'

        writer = csv.writer(response)
        writer.writerow(['Product', 'Full Name', 'Address', 'Phone Number', 'Comment', 'Quantity', 'Order Date', 'Is Paid'])  # CSV Header

        for order in queryset:
            writer.writerow([
                order.product.name,
                order.full_name,
                order.address,
                order.phone_number,
                order.comment,
                order.quantity,
                order.order_date,
                order.is_paid,
            ])  # CSV Data

        return response

    export_as_csv.short_description = "Export Selected Orders as CSV"

    # Adding the action to the admin
    actions = ['export_as_csv']

    def save_model(self, request, obj, form, change):
        try:
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            form.add_error(None, e)
            raise

class ProductAdmin(ModelAdmin):
    model = Product
    list_display = (
        'name',
        'short_description',
        'quantity',
        'image_preview',
        'price',
        'date_added'
    )
    list_filter = ('name', 'price', 'date_added')
    search_fields = ('name', 'price', 'date_added')
    ordering = ('-date_added',)

    def short_description(self, obj):
        return obj.description if len(obj.description) <= 50 else f"{obj.description[:50]}..."
    short_description.short_description = 'Description'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Image Preview'

    def export_as_csv(self, request, queryset):
        # Create the response object for CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="products.csv"'

        writer = csv.writer(response)
        writer.writerow(['Name', 'Description', 'Quantity', 'Price', 'Date Added'])  # CSV Header

        for product in queryset:
            writer.writerow([product.name, product.description, product.quantity, product.price, product.date_added])  # CSV Data

        return response

    export_as_csv.short_description = "Export Selected as CSV"

    # Adding the action to the admin
    actions = ['export_as_csv']

class CategoryAdmin(ModelAdmin):
    model = Category
    list_display = ('name', )
    list_filter = ('name', )
    search_fields = ('name', )

class SubcategoryAdmin(ModelAdmin):
    model = Subcategory
    list_display = ('name', 'category', )
    list_filter = ('name', 'category', )
    search_fields = ('name', 'category',)

class BrandAdmin(ModelAdmin):
    model = Brand
    list_display = ('name', 'subcategory', )
    list_filter = ('name', 'subcategory', )
    search_fields = ('name', 'subcategory',)

class ProductModelAdmin(ModelAdmin):
    model = ProductModel
    list_display = ('name', 'brand', 'subcategory', )
    list_filter = ('name', 'brand', 'subcategory', )
    search_fields = ('name', 'brand', 'subcategory',)

class StockAdmin(ModelAdmin):
    model = Stock
    list_display = ('product', 'quantity_in_stock', 'restock_date', 'added_by')  # Display the fields we have
    list_filter = ('product', 'quantity_in_stock', 'restock_date', 'added_by')  # Filterable fields
    search_fields = ('product__name', 'quantity_in_stock', 'restock_date')  # Searchable fields

    actions = ['restock_items']

    def restock_items(self, request, queryset):
        for stock in queryset:
            stock.quantity_in_stock += 10
            stock.save()

    restock_items.short_description = "Restock selected items"

    def save_model(self, request, obj, form, change):
        if not obj.added_by:
            obj.added_by = request.user

        obj.clean()
        super().save_model(request, obj, form, change)

admin.site.register(Order, OrderAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Subcategory, SubcategoryAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(ProductModel, ProductModelAdmin)
admin.site.register(Stock, StockAdmin)

admin.site.site_header = "Store Administration"
admin.site.site_title = "Shop Admin Portal"
admin.site.index_title = "Welcome to the Shop Admin Dashboard"
