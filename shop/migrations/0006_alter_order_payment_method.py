# Generated by Django 5.1.1 on 2024-09-17 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_alter_product_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('chapa', 'Chapa'), ('cbe', 'Commercial Bank of Ethiopia'), ('boa', 'Bank of Abyssinia'), ('awash', 'Awash Bank'), ('enat', 'Enat Bank'), ('dashen', 'Dashen Bank'), ('telebirr', 'Telebirr')], default='cbe', max_length=10),
        ),
    ]
