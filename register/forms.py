from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from paymentApp.BL_transactions import get_converted_amount
from .models import Profile


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    currency = forms.CharField(label='Currency', widget=forms.Select(choices=[
        ('GBP', 'Pound (£)'),
        ('USD', 'Dollar ($)'),
        ('EURO', 'Euro (€)'),
    ]))

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "currency", "password1", "password2"]

    # Save method overriding, for saving extra information in Registration Profile using 1-1 relation
    def save(self, request):
        user = super(RegistrationForm, self).save()

        # Saving Registration Profile with User, Currency and Balance.
        currency = self.cleaned_data['currency']
        balance = get_converted_amount('GBP', currency, 1000, parm=request)

        Profile(user=user, currency=currency, balance=balance).save()
        return user


class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        field = ['email', 'password1']
