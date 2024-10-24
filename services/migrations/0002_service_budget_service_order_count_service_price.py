# Generated by Django 5.1.2 on 2024-10-22 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='budget',
            field=models.PositiveIntegerField(default=5000),
        ),
        migrations.AddField(
            model_name='service',
            name='order_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='service',
            name='price',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
