from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):
    address = models.CharField(max_length=150)


    def __str__(self):
        return self.username
