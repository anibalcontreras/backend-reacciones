# Generated by Django 5.1.2 on 2024-10-22 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_order_total_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_rated',
            field=models.BooleanField(default=False),
        ),
    ]
