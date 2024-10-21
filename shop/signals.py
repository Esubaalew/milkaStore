import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Stock, Order, Telegram
from django.conf import settings
from io import BytesIO
import mimetypes
from django.core.exceptions import ValidationError
import json


# Your bot token and channel ID
BOT_TOKEN = 'TOKEN'
CHANNEL_ID = '-CHANNEL_ID'


@receiver(post_save, sender=Telegram)
def send_telegram_post(sender, instance, created, **kwargs):
    if created:
        stock = instance.stock
        product = stock.product

        URL = settings.SITE_URL
        image_url = URL + product.image.url if product.image else None

        caption = (
            f"<b>New Stock Added for {product.name}</b>\n\n"
            f"<b>Brand:</b> {product.brand.name}\n"
            f"<b>Model:</b> {product.model.name}\n"
            f"<b>Category:</b> {product.category.name}\n"
            f"<b>Quantity Available:</b> {stock.quantity_in_stock}\n"
            f"<b>Price:</b> {product.price}\n\n"
            f"<i>{product.description}</i>\n"
        )

        direct_link = f"https://t.me/StoreNowBot/mystore?startapp=product-{product.id}"

        data = {
            'chat_id': CHANNEL_ID,
            'caption': caption,
            'parse_mode': 'HTML',
            'reply_markup': json.dumps({
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
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    image_extension = product.image.url.split('.')[-1]
                    mime_type, _ = mimetypes.guess_type(image_url)

                    if not mime_type:
                        mime_type = image_response.headers.get('Content-Type', 'application/octet-stream')

                    image_data = BytesIO(image_response.content)

                    files = {
                        'photo': (f'image.{image_extension}', image_data, mime_type)
                    }
                    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto'
                    response = requests.post(url, data=data, files=files)
                else:
                    print(f"Failed to download image: {image_response.status_code}")
                    return
            else:
                url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
                data['text'] = caption
                response = requests.post(url, json=data)

            if response.status_code == 200:
                print(f"Post sent successfully to Telegram for product {product.name}")
            else:
                print(f"Failed to send message to Telegram: {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")



@receiver(post_save, sender=Order)
def reduce_stock_on_payment(sender, instance, **kwargs):
    """
    Signal to reduce stock when an order is marked as paid.
    This will reduce the stock quantity based on the order quantity.
    """

    if instance.is_paid:
        try:

            stock = Stock.objects.get(product=instance.product)


            if stock.quantity_in_stock >= instance.quantity:

                stock.quantity_in_stock -= instance.quantity
                stock.save()
            else:

                raise ValidationError("Not enough stock available.")
        except Stock.DoesNotExist:

            raise ValidationError(f"Stock entry for product '{instance.product}' does not exist.")

