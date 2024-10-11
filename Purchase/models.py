from django.db import models
from datetime import datetime

# Category model
class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# Subcategory model
class Subcategory(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category, related_name='subcategories', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.category.name} - {self.name}"


# Brand model
class Brand(models.Model):
    name = models.CharField(max_length=255)
    subcategory = models.ForeignKey(
        Subcategory, related_name='brands', on_delete=models.CASCADE, default=1)

    def __str__(self):
        return f"{self.subcategory.name} - {self.name}"


# ProductModel (renamed from Model) under a brand
class ProductModel(models.Model):  # Renamed class
    name = models.CharField(max_length=255)
    brand = models.ForeignKey(
        Brand, related_name='models', on_delete=models.CASCADE)
    subcategory = models.ForeignKey(
        Subcategory, related_name='models', on_delete=models.CASCADE, default=1)

    def __str__(self):
        return f"{self.brand.name} - {self.name}"


# Item model
class Product(models.Model):
    name = models.CharField(max_length=255)
    subcategory = models.ForeignKey(
        Subcategory, related_name='items', on_delete=models.CASCADE)
    brand = models.ForeignKey(
        Brand, related_name='items', on_delete=models.CASCADE)
    model = models.ForeignKey(
        ProductModel, related_name='items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    data_added = models.DateTimeField(default=datetime.now)


    def __str__(self):
        return self.name
