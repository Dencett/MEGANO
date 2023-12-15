# Generated by Django 4.2.7 on 2023-12-13 16:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0003_alter_category_slug_category_unique_parent_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="LimitedOffer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("end_date", models.DateTimeField(verbose_name="дата окончания")),
                ("archived", models.BooleanField(default=False, verbose_name="архивировано")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="products.product")),
            ],
            options={
                "verbose_name": "ограниченное предложение",
                "verbose_name_plural": "ограниченные предложения",
            },
        ),
    ]
