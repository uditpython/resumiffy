# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models

from django.contrib.auth.models import User

# Create your models here.
class UserProfile(User):
    
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True,null=True)
    birth_date = models.DateField(null=True, blank=True)