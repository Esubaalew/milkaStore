from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'address', 'phone_number', 'comment', 'quantity']


class ReceiptUploadForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['payment_method', 'receipt_file']
        widgets = {
            'payment_method': forms.RadioSelect(choices=Order.PAYMENT_METHODS),
        }