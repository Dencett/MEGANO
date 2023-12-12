# Generated by Django 4.2.7 on 2023-12-11 18:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0003_order_discount_amount_alter_order_total_price_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="total_price",
            field=models.DecimalField(decimal_places=2, max_digits=12, verbose_name="общая стоимость"),
        ),
    ]