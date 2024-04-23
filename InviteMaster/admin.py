from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile
from django.contrib.auth.forms import UserCreationForm



admin.site.register(UserProfile)

