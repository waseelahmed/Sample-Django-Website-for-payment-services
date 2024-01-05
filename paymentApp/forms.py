from django import forms
from django.contrib.auth.models import User
from django.forms import NumberInput
from django.utils.datetime_safe import datetime
from register.models import Profile
from .models import Transactions
from .BL_transactions import Transaction_BL

bl_object = Transaction_BL()


class TransactionForm(forms.Form):
    def __init__(self, data=None, user=None, action=None):
        super(TransactionForm, self).__init__(data)
        self.user = user
        self.action = action
        currency = bl_object.currency_sign
        self.fields['amount'].widget.attrs['placeholder'] = currency[Profile.objects.get(user_id=user.id).currency]

    receiver_username = forms.CharField(max_length=20, required=True, label="Username")
    title = forms.CharField(max_length=100, required=True, )
    amount = forms.DecimalField(required=True, min_value=1, max_value=10000)

    def clean(self):
        # Running all cleaning checks
        cleaned_data = super().clean()

        receiver_username = cleaned_data.get("receiver_username")
        amount = cleaned_data.get("amount")

        # If no such user exists then throw an error
        if not User.objects.filter(username=receiver_username).exists():
            raise forms.ValidationError(
                bl_object.validation_error[404]
            )

        if self.user.username == receiver_username:
            raise forms.ValidationError(
                bl_object.validation_error[400]
            )
        if amount >= Profile.objects.get(user_id=self.user.id).balance and self.action == 'Direct':
            raise forms.ValidationError(
                bl_object.validation_error[401]
            )

    class Meta:
        model = Transactions
        fields = ["receiver_username", "amount", "title"]


class FilterForm(forms.Form):
    def __init__(self, data=None):
        super(FilterForm, self).__init__(data)
        self.filter_applied = False
        self.start_date = None
        self.end_date = None

    Start_date = forms.DateTimeField(required=False, label="Start date", widget= NumberInput(attrs={'class':'mr-5','type': 'date'}))
    End_date = forms.DateTimeField(required=False, label="End date", widget=NumberInput(attrs={'type': 'date'}))

    def clean(self):
        cleaned_data = super().clean()
        self.start_date = cleaned_data.get("Start_date")
        self.end_date = cleaned_data.get("End_date")

        if self.start_date is None and self.end_date is None:
            self.filter_applied = False
        else:
            self.filter_applied = True

        if self.start_date is None:
            self.start_date = datetime.date(datetime.min)
        else:
            self.start_date = datetime.date(self.start_date)

        if self.end_date is None:
            self.end_date = datetime.date(datetime.today())
        else:
            self.end_date = datetime.date(self.end_date)

        if self.start_date > datetime.date(datetime.today()):
            self.filter_applied = False
            self.add_error("Start_date", "Date should be in past. Filter cannot be applied." )

        if self.end_date > datetime.date(datetime.today()):
            self.filter_applied = False
            self.add_error("End_date", "Date should be in past. Filter cannot be applied." )

        if self.filter_applied and self.end_date < self.start_date:
            self.filter_applied = False
            self.add_error("Start_date", "Please enter valid date range. Filter cannot be applied" )

    class Meta:
        fields = ["Start_date", "End_date"]
