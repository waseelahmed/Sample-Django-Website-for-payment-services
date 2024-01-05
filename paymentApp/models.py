from django.db import models
from django.contrib.auth.models import User


class Transactions(models.Model):
    title = models.fields.CharField(max_length=100)
    create_at = models.DateField(auto_now_add=True)
    time = models.fields.TimeField(auto_now_add=True)

    transferred_amount = models.fields.DecimalField(max_digits=10000, decimal_places=2)
    sender_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    request_type = models.fields.CharField(max_length=100, null=True, default='direct')
    received_amount = models.fields.DecimalField(max_digits=10000, decimal_places=2, default=0)

    def __str__(self):
        return f"Transaction#:{self.pk}"


class Transaction_Receiver(models.Model):
    transaction = models.ForeignKey(Transactions, on_delete=models.CASCADE, related_name='receiver')
    balance = models.fields.DecimalField(max_digits=10000, decimal_places=2)
    new_balance = models.fields.DecimalField(max_digits=10000, decimal_places=2)
    currency = models.fields.CharField(max_length=10)


class Transaction_Sender(models.Model):
    transaction = models.ForeignKey(Transactions, on_delete=models.CASCADE, related_name='sender')
    balance = models.fields.DecimalField(max_digits=10000, decimal_places=2)
    new_balance = models.fields.DecimalField(max_digits=10000, decimal_places=2)
    currency = models.fields.CharField(max_length=10)


class Request(models.Model):
    title = models.fields.CharField(max_length=100)
    create_at = models.DateField(auto_now_add=True)
    time = models.fields.TimeField(auto_now_add=True)

    requested_amount = models.fields.DecimalField(max_digits=10000, decimal_places=2)
    # Need to save currency because the user might change the currency after the request.
    requested_currency = models.fields.CharField(max_length=100, default='')

    request_sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='request_sender')
    request_receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='request_receiver')
    request_answer = models.fields.CharField(max_length=20)
    request_trans = models.fields.IntegerField(null=True)
    response = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Request#:{self.pk}"

