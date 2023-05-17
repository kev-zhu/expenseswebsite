from django.contrib import admin
from .models import UserIncome, Source
# Register your models here.

admin.site.register(Source)
admin.site.register(UserIncome)