from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .forms import UserCreationForm, UserChangeForm
from .models import User

class UserAdmin(DjangoUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ["username", "email"]

admin.site.register(User, UserAdmin)