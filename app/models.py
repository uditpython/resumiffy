# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User



class UserProfile(User):
    
    role = models.TextField(max_length=500, blank=True)
  
# Create your models here.

