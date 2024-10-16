from django import forms
from django.contrib import admin
from unfold.admin import ModelAdmin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from django.utils.html import format_html
from unfold.contrib.import_export.forms import SelectableFieldsExportForm, ImportForm
from .models import Order, Product, Category, Subcategory, Brand, ProductModel, Stock
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


# Define a resource for the Order model
class OrderResource(resources.ModelResource):
    class Meta:
        model = Order

# Define a custom form for date range selection during export
class DateRangeExportForm(SelectableFieldsExportForm):
    start_date = forms.DateField(required=False, label=_("Start date"), widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, label=_("End date"), widget=forms.DateInput(attrs={'type': 'date'}))

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError(_("Start date cannot be later than end date."))

        return cleaned_data



class OrderAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = OrderResource
    import_form_class = ImportForm
    export_form_class = DateRangeExportForm

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

    def get_export_queryset(self, request):
        """
        Filter the queryset based on the date range provided in the export form.
        """
        queryset = super().get_export_queryset(request)
        form = self.export_form(request.POST or None)
        if form.is_valid():
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')

            if start_date:
                queryset = queryset.filter(order_date__gte=start_date)
            if end_date:
                queryset = queryset.filter(order_date__lte=end_date)

        return queryset

    def save_model(self, request, obj, form, change):
        try:
            # Call the original save method
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            # If a ValidationError is raised, add it to the form errors
            form.add_error(None, e)
            # Re-raise the error to prevent saving
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
