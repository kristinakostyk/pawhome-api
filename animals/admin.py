from django.contrib import admin

# Register your models here.
from .models import Animal, Shelter

admin.site.register(Shelter)
admin.site.register(Animal)
