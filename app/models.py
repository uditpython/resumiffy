# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User
from phone_field import PhoneField


class UserProfile(User):
    
    role = models.TextField(max_length=500, blank=True)
    address = models.TextField(max_length=500, blank=True,null=True)
    phone =  models.CharField(max_length=12,blank=True,null=True)
# Create your models here.

