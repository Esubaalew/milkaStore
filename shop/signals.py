import requests
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Stock, Order
from django.conf import settings
from io import BytesIO
import mimetypes
import json


# Your bot token and channel ID
BOT_TOKEN = 'TOKEN'
CHANNEL_ID = '-CHANNEL_ID'


@receiver(post_save, sender=Stock)
def send_stock_to_channel(sender, instance, created, **kwargs):
    print("Signal triggered!")

    URL = settings.SITE_URL

    product = instance.product
    image_url = URL + product.image.url if product.image else None
    print(f"Image URL: {image_url}")  # Debugging image URL

    caption = (
        f"<b>New Stock Added for {product.name}</b>\n\n"
        f"<b>Brand:</b> {product.brand.name}\n"
        f"<b>Model:</b> {product.model.name}\n"
        f"<b>Category:</b> {product.category.name}\n"
        f"<b>Quantity Available:</b> {instance.quantity_in_stock}\n"
        f"<b>Price:</b> {product.price}\n\n"
        f"<i>{product.description}</i>\n"
    )

    direct_link = f"https://t.me/StoreNowBot/mystore?startapp=product-{product.id}"

    data = {
        'chat_id': CHANNEL_ID,
        'caption': caption,
        'parse_mode': 'HTML',
        'reply_markup': json.dumps({  # Convert reply_markup to JSON
            'inline_keyboard': [
                [
                    {
                        'text': 'Order Now',
                        'url': direct_link
                    }
                ]
            ]
        })
    }

    try:
        if image_url:
            # Download the image from the URL
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                # Detect the file extension and MIME type
                image_extension = product.image.url.split('.')[-1]  # Get file extension from the URL
                mime_type, _ = mimetypes.guess_type(image_url)

                # Fallback to response header if mimetypes module doesn't detect the type
                if not mime_type:
                    mime_type = image_response.headers.get('Content-Type', 'application/octet-stream')

                # Load the image into memory
                image_data = BytesIO(image_response.content)

                # Send the image as a file to Telegram
                files = {
                    'photo': (f'image.{image_extension}', image_data, mime_type)
                }
                url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto'
                response = requests.post(url, data=data, files=files)
            else:
                print(f"Failed to download image: {image_response.status_code}")
                return
        else:
            # Send as a text message if no image is available
            url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
            data['text'] = caption
            response = requests.post(url, json=data)

        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")

        if response.status_code != 200:
            print(f"Failed to send message to Telegram: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")


@receiver(pre_save, sender=Order)
def check_order_is_paid(sender, instance, **kwargs):
    if instance.pk:
        previous_order = Order.objects.get(pk=instance.pk)
        instance._previous_is_paid = previous_order.is_paid
    else:
        instance._previous_is_paid = False


# Post-save signal to handle quantity decrease
@receiver(post_save, sender=Order)
def update_product_quantity(sender, instance, created, **kwargs):
    if instance.is_paid and not instance._previous_is_paid:
        try:
            product = instance.product
            if product.quantity >= instance.quantity:
                product.quantity -= instance.quantity
                product.save()
            else:
                raise ValueError("Not enough product quantity available to fulfill the order.")
        except Exception as e:
            print(f"Error updating product quantity: {str(e)}")
