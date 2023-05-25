from django.contrib import admin
from .models import *

models = [
    Project,
    Role,
    Collaboration,
    Task,

]

admin.register(models)
