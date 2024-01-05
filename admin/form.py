from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class AdminUserCreationForm(UserCreationForm):
    username = forms.CharField(max_length=30)

    class Meta:
        model = User
        fields = ['username', 'email']

    # Overiding save method to create a super user.
    def save(self):
        user = super(AdminUserCreationForm, self).save()
        User.objects.filter(username=user).update(is_staff=True, is_superuser=True)
