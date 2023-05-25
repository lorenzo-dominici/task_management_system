from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView as DjangoLogoutView
from django.views.generic.edit import CreateView
from .forms import LoginForm, UserCreationForm

class LoginView(DjangoLoginView):
    template_name = 'auth/login.html'
    authentication_form = LoginForm

class LogoutView(DjangoLogoutView):
    template_name = 'auth/logout.html'

class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'auth/register.html'
    success_url = reverse_lazy('home')
