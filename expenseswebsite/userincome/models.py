from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
# Create your models here.

class UserIncome(models.Model):
    amount = models.FloatField()
    date = models.DateField(default=now)  
    description = models.TextField()
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    source = models.CharField(max_length=255)

    def __str__(self):
        return self.owner.username + ' - ' + self.source

    class Meta:
        ordering = ['-date']
        verbose_name_plural = "User Income"


class Source(models.Model):
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.owner.username + ' - ' + self.name