from django import forms
from django.contrib import admin
from unfold.admin import ModelAdmin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import Order, Product
from django.utils.html import format_html
from unfold.contrib.import_export.forms import ExportForm, ImportForm, SelectableFieldsExportForm

# Define a resource for the Order model
class OrderResource(resources.ModelResource):
    class Meta:
        model = Order

class OrderAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = OrderResource  # Specify the resource class for import/export
    import_form_class = ImportForm  # Use the form provided by Unfold for import
    export_form_class = SelectableFieldsExportForm  # Allow selection of fields to export

    model = Order
    list_display = (
        'product_name',
        'full_name',
        'address',
        'phone_number',
        'comment',
        'quantity',
        'order_date'
    )
    list_filter = (
        'product',
        'full_name',
        'address',
        'phone_number',
        'quantity',
        'order_date'
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

class ProductAdmin(ModelAdmin):  # Inherit from Unfold Admin's ModelAdmin
    model = Product
    list_display = (
        'name',
        'short_description',
        'image_preview',  # Update to use image_preview method
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

# Registering the models
admin.site.register(Order, OrderAdmin)
admin.site.register(Product, ProductAdmin)

# Change the title and header of the admin site
admin.site.site_header = "Store Administration"
admin.site.site_title = "Shop Admin Portal"
admin.site.index_title = "Welcome to the Shop Admin Dashboard"
