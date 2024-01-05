from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    currency = models.fields.CharField(max_length=10)
    balance = models.fields.DecimalField(decimal_places=2, max_digits=100000)

    mobile = models.fields.CharField(max_length=13, default='', null=True)
    address_1 = models.fields.CharField(max_length=50, default='', null=True)
    address_2 = models.fields.CharField(max_length=50, default='', null=True)
    post_code = models.fields.CharField(max_length=7, default='', null=True)
    state = models.fields.CharField(max_length=50, default='', null=True)
    area = models.fields.CharField(max_length=50, default='', null=True)
    country = models.fields.CharField(max_length=50, default='', null=True)
    region = models.fields.CharField(max_length=50, default='', null=True)

    def __str__(self):
        return self.user.username
