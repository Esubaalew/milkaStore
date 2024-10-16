from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# Category model
class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# Subcategory model
class Subcategory(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(
        'Category', related_name='subcategories', on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return f"{self.category.name} - {self.name}" if self.category else self.name

    def save(self, *args, **kwargs):

        if not self.category:
            raise ValueError("Category must be specified for the subcategory.")
        super(Subcategory, self).save(*args, **kwargs)


# Brand model
class Brand(models.Model):
    name = models.CharField(max_length=255)
    subcategory = models.ForeignKey(
        'Subcategory', related_name='brands', on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return f"{self.subcategory.name} - {self.name}" if self.subcategory else self.name

    def save(self, *args, **kwargs):
        # Ensure that the subcategory is not missing
        if not self.subcategory:
            raise ValueError("Subcategory must be specified for the brand.")
        super(Brand, self).save(*args, **kwargs)



# ProductModel (renamed from Model) under a brand
class ProductModel(models.Model):  # Renamed class to avoid conflict with Django's `Model` class
    name = models.CharField(max_length=255)
    brand = models.ForeignKey(
        'Brand', related_name='models', on_delete=models.CASCADE, null=True, blank=True
    )
    subcategory = models.ForeignKey(
        'Subcategory', related_name='models', on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return f"{self.brand.name} - {self.name}" if self.brand else self.name

    def save(self, *args, **kwargs):
        # Ensure that the brand and subcategory are not missing
        if not self.brand or not self.subcategory:
            raise ValueError("Both Brand and Subcategory must be specified for the product model.")
        super(ProductModel, self).save(*args, **kwargs)



class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(
        'Category', related_name='items', on_delete=models.CASCADE, null=True, blank=True
    )
    subcategory = models.ForeignKey(
        'Subcategory', related_name='items', on_delete=models.CASCADE, null=True, blank=True
    )
    brand = models.ForeignKey(
        'Brand', related_name='items', on_delete=models.CASCADE, null=True, blank=True
    )
    model = models.ForeignKey(
        'ProductModel', related_name='items', on_delete=models.CASCADE, null=True, blank=True
    )
    quantity = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date_added = models.DateTimeField(default=datetime.now)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_added']
        verbose_name = "Purchase"
        verbose_name_plural = "Purchases"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Ensure that required foreign keys are not missing
        if not self.category or not self.subcategory or not self.brand or not self.model:
            raise ValueError("Category, Subcategory, Brand, and Model must be specified.")
        super(Product, self).save(*args, **kwargs)

class Order(models.Model):
    PAYMENT_METHODS = [
        ('chapa', 'Chapa'),
        ('cbe', 'Commercial Bank of Ethiopia'),
        ('boa', 'Bank of Abyssinia'),
        ('awash', 'Awash Bank'),
        ('enat', 'Enat Bank'),
        ('dashen', 'Dashen Bank'),
        ('telebirr', 'Telebirr'),
        ('cash', 'Cash'),
    ]
    ORDER_TYPES = [
        ('manual', 'manual'),
        ('online', 'online'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order_type = models.CharField(max_length=10, choices=ORDER_TYPES, default='manual')
    full_name = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    comment = models.TextField(blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)  # Default quantity is 1
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # New field for total price
    order_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='cbe')
    payment_ref = models.CharField(max_length=100, blank=True, null=True, help_text="Enter the payment reference code")
    is_paid = models.BooleanField(default=False)

    class Meta:
        ordering = ['-order_date']
        verbose_name = "Sale"
        verbose_name_plural = "Sales"

    def save(self, *args, **kwargs):

        self.total_price = self.product.price * self.quantity
        super(Order, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} pcs"


# Stock model for product inventory
class Stock(models.Model):
    product = models.ForeignKey(Product, related_name='stocks', on_delete=models.CASCADE)
    quantity_in_stock = models.PositiveIntegerField()
    restock_date = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Stock for {self.product.name} - {self.quantity_in_stock} units"

    class Meta:
        verbose_name = "Store"
        verbose_name_plural = "Stores"

    def clean(self):

        if self.quantity_in_stock <= 0:
            raise ValidationError("Stock quantity cannot be zero or negative.")

        if self.product.quantity is None:
            raise ValidationError(f"The product '{self.product.name}' does not have a set quantity.")

        if self.quantity_in_stock is None:
            raise ValidationError(f"The stock quantity for '{self.product.name}' cannot be empty.")

        if self.quantity_in_stock > self.product.quantity:
            raise ValidationError(
                f"You cannot add more stock than the available product of {self.product.quantity} units."
            )

    def save(self, *args, **kwargs):
        if self.quantity_in_stock is None:
            self.quantity_in_stock = self.product.quantity

        super().save(*args, **kwargs)