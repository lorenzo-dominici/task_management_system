from django.contrib import admin
from .models import *

models = [
    Project,
    Role,
    Collaboration,
    Task,
    TaskRole,
    Assignation,
    JoinRequest
]

admin.site.register(models)
