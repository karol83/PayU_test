# Generated by Django 2.0.13 on 2019-03-14 13:02

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_remove_order_external_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='Transaction id'),
        ),
    ]
