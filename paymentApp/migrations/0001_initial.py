# Generated by Django 4.1.7 on 2023-04-24 15:40

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
            name='Transactions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('create_at', models.DateField(auto_now_add=True)),
                ('time', models.TimeField(auto_now_add=True)),
                ('transferred_amount', models.DecimalField(decimal_places=2, max_digits=10000)),
                ('request_type', models.CharField(default='direct', max_length=100, null=True)),
                ('received_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10000)),
                ('receiver_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to=settings.AUTH_USER_MODEL)),
                ('sender_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction_Sender',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.DecimalField(decimal_places=2, max_digits=10000)),
                ('new_balance', models.DecimalField(decimal_places=2, max_digits=10000)),
                ('currency', models.CharField(max_length=10)),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to='paymentApp.transactions')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction_Receiver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.DecimalField(decimal_places=2, max_digits=10000)),
                ('new_balance', models.DecimalField(decimal_places=2, max_digits=10000)),
                ('currency', models.CharField(max_length=10)),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to='paymentApp.transactions')),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('create_at', models.DateField(auto_now_add=True)),
                ('time', models.TimeField(auto_now_add=True)),
                ('requested_amount', models.DecimalField(decimal_places=2, max_digits=10000)),
                ('requested_currency', models.CharField(default='', max_length=100)),
                ('request_answer', models.CharField(max_length=20)),
                ('request_trans', models.IntegerField(null=True)),
                ('response', models.DateTimeField(blank=True, null=True)),
                ('request_receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='request_receiver', to=settings.AUTH_USER_MODEL)),
                ('request_sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='request_sender', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
