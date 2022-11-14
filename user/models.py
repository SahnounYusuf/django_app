from django.contrib.auth.models import User
from django.db import models


class Employee(models.Model):
    username = models.CharField(max_length=150)
    password = models.TextField(max_length=80)
    role = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=50)
    country = models.CharField(max_length=150)
    company = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.username}, {self.role}, {self.email}"


class Users(User):
    role = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.username}, {self.role}"

    def is_admin(self) -> bool:
        return True if self.role == 'Admin' else False
