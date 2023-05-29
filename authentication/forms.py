from django import forms
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm, UserChangeForm as DjangoUserChangeForm
from django.contrib.auth.forms import AuthenticationForm

from .models import User

class UserCreationForm(DjangoUserCreationForm):

    class Meta:
        model = User
        fields = (
            "username",
            "email"
        )

class UserChangeForm(DjangoUserChangeForm):

    class Meta:
        model = User
        fields = (
            "username",
            "email"
        )


class LoginForm(AuthenticationForm):
    pass
