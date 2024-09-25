import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product
from django.conf import settings

# Your bot token and channel ID
BOT_TOKEN = '7543719732:AAH8cIPr_xv9oaxtzw21EmnDd0LhJXVfCPs'
CHANNEL_ID = '-1002437698028'


@receiver(post_save, sender=Product)
def send_product_to_channel(sender, instance, created, **kwargs):
    URL = settings.SITE_URL
    if created:
        # Image URL
        image_url = URL + instance.image.url

        caption = (
            f"<b>{instance.name}</b>\n\n"
            f"<i>{instance.description}</i>\n\n"
            f"<b>Price:</b> {instance.price}\n"
        )

        direct_link = f"https://t.me/StoreNowBot/mystore?startapp=product-{instance.id}"

        url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto'

        data = {
            'chat_id': CHANNEL_ID,
            'photo': image_url,
            'caption': caption,
            'parse_mode': 'HTML',
            'reply_markup': {
                'inline_keyboard': [
                    [
                        {
                            'text': 'Order Now',
                            'url': direct_link
                        }
                    ]
                ]
            }
        }

        response = requests.post(url, json=data)

        print(response.json())
