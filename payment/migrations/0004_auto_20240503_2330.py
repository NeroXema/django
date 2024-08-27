# Generated by Django 3.2 on 2024-05-03 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_order_alter_shippingaddress_shipping_address2_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='date_order',
            new_name='date_ordered',
        ),
        migrations.AddField(
            model_name='order',
            name='shipped',
            field=models.BooleanField(default=False),
        ),
    ]
