from rest_framework import viewsets, permissions
from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ReceiptUploadForm
import logging
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

@method_decorator(csrf_exempt, name='dispatch')
class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ValidationError
from .models import Product, Order
from .forms import ReceiptUploadForm
import logging

logger = logging.getLogger(__name__)

@csrf_protect
def webapp_view(request):
    logger.info(f"Request Method: {request.method}")
    logger.info(f"Query Parameters: {request.GET}")

    start_param = request.GET.get('tgWebAppStartParam', '')
    logger.info(f"Start Parameter: {start_param}")

    # Validate the start_param to ensure it contains a valid product ID
    if start_param.startswith('product-'):
        try:
            product_id = start_param.split('-')[1]
            logger.info(f"Product ID extracted: {product_id}")

            product = get_object_or_404(Product, id=product_id)
            logger.info(f"Product found: {product.name} (ID: {product.id})")

            # Ensure the product has stock available
            if product.quantity < 1:
                logger.error(f"Product ID {product_id} is out of stock.")
                return render(request, 'webapp.html', {
                    'product': product,
                    'error': 'This product is currently out of stock.',
                })

        except (IndexError, ValueError):
            logger.error("Error extracting product ID from start_param")
            return render(request, '404.html', {
                'error': 'Invalid product ID provided. Please check the URL or select a valid product.'
            })
    else:
        logger.error("Invalid start_param, does not start with 'product-'")
        return render(request, '404.html', {
            'error': 'Product not found. Please check the URL and try again.'
        })

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')
        comment = request.POST.get('comment', '')
        quantity = int(request.POST.get('quantity', 1))
        payment_method = request.POST.get('payment_method', 'cbe')

        # Create the order object first to validate the quantity
        order = Order(
            product=product,
            full_name=full_name,
            address=address,
            phone_number=phone_number,
            comment=comment,
            quantity=quantity,
            payment_method=payment_method,
            is_paid=False,
            order_type='online'
        )

        try:
            # Validate the order before saving
            # order.full_clean()  # Calls the clean() method for validation
            order.save()  # Save if clean passes
            logger.info(f"Order created successfully for {product.name}, Quantity: {quantity}")
            return redirect('payment_choice', order_id=order.id)
        except ValidationError as e:
            # Capture and extract a friendly error message
            error_message = e.message_dict.get('__all__', ['An error occurred'])[0]
            logger.error(f"Validation error: {error_message}")
            return render(request, 'webapp.html', {
                'product': product,
                'error': error_message,  # Pass the friendly message to the template
            })

    logger.info(f"Rendering product page for product: {product.name}")
    return render(request, 'webapp.html', {'product': product})


@csrf_protect
def payment_choice_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    print(order.product)

    # Debug log to check if the order has a valid product
    if not order.product:
        logger.error(f"Order ID {order_id} has no product associated with it.")
        return render(request, '404.html', {
            'error': 'This order does not have an associated product.'
        })

    if request.method == 'POST':
        form = ReceiptUploadForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data.get('payment_method')
            payment_ref = form.cleaned_data.get('payment_ref')

            order.payment_method = payment_method
            order.payment_ref = payment_ref
            order.save()

            return render(request, 'payment_success.html', {'order': order})
    else:
        form = ReceiptUploadForm(instance=order)

    return render(request, 'payment_choice.html', {'form': form, 'order': order})

def custom_404_view(request, exception):
    return render(request, '404_custom.html', status=404)
