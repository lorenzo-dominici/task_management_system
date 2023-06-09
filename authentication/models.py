from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):

    email = models.EmailField(unique=True)

    class Meta:
        ordering = ['username']
    
    def __str__(self):
        return self.username
