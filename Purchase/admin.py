from django.contrib import admin
from unfold.admin import ModelAdmin
from import_export.admin import ImportExportModelAdmin

from .models import Category, Subcategory, Brand, ProductModel, Product


# Inline for Subcategory in Category Admin
class SubcategoryInline(admin.TabularInline):  # You can also use admin.StackedInline
    model = Subcategory
    extra = 1  # Number of empty forms to display

# Category Admin with Unfold and ImportExport functionality
@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin, ModelAdmin):
    inlines = [SubcategoryInline]
    search_fields = ('name',)
    ordering = ('name',)

# Inline for Brand in Subcategory Admin
class BrandInline(admin.TabularInline):
    model = Brand
    extra = 1

@admin.register(Subcategory)
class SubcategoryAdmin(ImportExportModelAdmin, ModelAdmin):  # Integrating Unfold ModelAdmin
    list_display = ('name', 'category')
    inlines = [BrandInline]  # Show Brand inline in Subcategory page
    search_fields = ('name', 'category__name')
    list_filter = ('category',)
    ordering = ('name',)

# Inline for ProductModel in Brand Admin
class ProductModelInline(admin.TabularInline):
    model = ProductModel
    extra = 1

# Brand Admin with Unfold functionality
@admin.register(Brand)
class BrandAdmin(ModelAdmin):  # Inherit from Unfold Admin's ModelAdmin
    list_display = ('name', 'subcategory')
    inlines = [ProductModelInline]  # Show ProductModel inline in Brand page
    search_fields = ('name', 'subcategory__name')
    list_filter = ('subcategory',)
    ordering = ('name',)

# Product Admin with Unfold functionality
@admin.register(Product)
class ProductAdmin(ModelAdmin):  # Inherit from Unfold Admin's ModelAdmin
    list_display = ('name', 'subcategory', 'brand', 'model')
    search_fields = ['name', 'subcategory__name', 'brand__name']
    list_filter = ('subcategory', 'brand')
