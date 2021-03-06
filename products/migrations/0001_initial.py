# Generated by Django 2.0.13 on 2019-03-13 12:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.UUIDField(verbose_name='Transaction id')),
                ('curtomer_ip', models.GenericIPAddressField(default='127.0.0.1', verbose_name='Client Ip Address')),
                ('status', models.CharField(choices=[('NEW', 'NEW'), ('PENDING', 'PENDING'), ('CANCELED', 'CANCELED'), ('COMPLETED', 'COMPLETED'), ('REJECTED', 'REJECTED')], default='NEW', max_length=9, verbose_name='Payment status')),
                ('status_date', models.DateField(blank=True, default=None, null=True, verbose_name='Payment confirmation date')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=127, verbose_name='Name')),
                ('desc', models.CharField(max_length=255, verbose_name='Description')),
                ('price', models.PositiveIntegerField(verbose_name='Price')),
                ('is_available', models.BooleanField(default=False, verbose_name='Available')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.Product', verbose_name='Product name'),
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
    ]
