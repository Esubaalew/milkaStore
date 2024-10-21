from django.db import models, transaction
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

    def clean(self):
        if not self.category:
            raise ValidationError("Category must be specified for the subcategory.")

    def save(self, *args, **kwargs):
        self.clean()  # Ensure validation is called on save
        super(Subcategory, self).save(*args, **kwargs)


# Brand model
class Brand(models.Model):
    name = models.CharField(max_length=255)
    subcategory = models.ForeignKey(
        'Subcategory', related_name='brands', on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return f"{self.subcategory.name} - {self.name}" if self.subcategory else self.name

    def clean(self):
        if not self.subcategory:
            raise ValidationError("Subcategory must be specified for the brand.")

    def save(self, *args, **kwargs):
        self.clean()  # Ensure validation is called on save
        super(Brand, self).save(*args, **kwargs)


# ProductModel (renamed from Model) under a brand
class ProductModel(models.Model):
    name = models.CharField(max_length=255)
    brand = models.ForeignKey(
        'Brand', related_name='models', on_delete=models.CASCADE, null=True, blank=True
    )
    subcategory = models.ForeignKey(
        'Subcategory', related_name='models', on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return f"{self.brand.name} - {self.name}" if self.brand else self.name

    def clean(self):
        if not self.brand or not self.subcategory:
            raise ValidationError("Both Brand and Subcategory must be specified for the product model.")

    def save(self, *args, **kwargs):
        self.clean()  # Ensure validation is called on save
        super(ProductModel, self).save(*args, **kwargs)


# Product model
class Product(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, blank=True, null=True, unique=True, help_text="Unique product code")
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
    def __str__(self):
        return self.name

    def clean(self):
        if not self.category or not self.subcategory or not self.brand or not self.model:
            raise ValidationError("Category, Subcategory, Brand, and Model must be specified.")

    def save(self, *args, **kwargs):
        self.clean()  # Call the clean method for validation

        # Use a transaction to ensure all operations succeed or fail together
        with transaction.atomic():
            # Check if it's a new product (no PK yet)
            is_new_product = self.pk is None

            # If not a new product, retrieve the old quantity before saving
            if not is_new_product:
                original_product = Product.objects.get(pk=self.pk)
                old_quantity = original_product.quantity
            else:
                old_quantity = 0

            super(Product, self).save(*args, **kwargs)  # Save the product first

            # Calculate how much new quantity is added
            added_quantity = self.quantity - old_quantity

            # Create a new Purchase entry for the added quantity (even if updated product)
            if added_quantity > 0:
                Purchase.objects.create(
                    product=self,
                    quantity_purchased=added_quantity,  # Track only the additional quantity
                    added_by=kwargs.get('user', None)  # Pass user if applicable
                )

            # Update or create the stock (Store) for this product
            stock, created = Stock.objects.get_or_create(product=self)
            if created:
                stock.quantity_in_stock = self.quantity
            else:
                stock.quantity_in_stock += added_quantity  # Increment stock by the new quantity

            stock.save()

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
    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("Quantity cannot be zero or negative.")

        if self.product.quantity is None:
            raise ValidationError(f"The product '{self.product.name}' does not have a set quantity.")

        # Check if the product has stock
        try:
            stock = Stock.objects.get(product=self.product)
        except Stock.DoesNotExist:
            raise ValidationError(f"Stock entry for product '{self.product.name}' does not exist. Make sure you add stock(Store) first.")


        if self.quantity > stock.quantity_in_stock:
                raise ValidationError(
                    f"You cannot order more than the available stock of {stock.quantity_in_stock} units."
                )

    def save(self, *args, **kwargs):
        self.clean()
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


class Purchase(models.Model):
    product = models.ForeignKey(Product, related_name='purchases', on_delete=models.CASCADE)
    quantity_purchased = models.PositiveIntegerField()
    purchase_date = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Purchase of {self.product.name} - {self.quantity_purchased} units"

class Telegram(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='telegram_posts')
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Telegram Post for {self.stock.product.name} - {self.date_posted}"

    class Meta:
        verbose_name = "Telegram Post"
        verbose_name_plural = "Telegram Posts"