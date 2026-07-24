from django.db import models

class Register(models.Model):
    name=models.CharField(max_length=50)
    username=models.CharField(max_length=50)
    email=models.EmailField(max_length=40)
    password=models.CharField(max_length=40)
    confirm_password=models.CharField(max_length=40)
    is_approved=models.BooleanField(default=False)
    def __str__(self):
        return self.name
    
