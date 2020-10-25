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


class OrderInfo(models.Model):
    order_id =  models.CharField(max_length=30)
    package = models.TextField(max_length=500, blank=True)
    email = models.CharField(max_length=30, blank=True,null=True)
    resume_worker = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    resume_url = models.CharField(max_length=100, blank=True,null=True)
    new_resume_url = models.CharField(max_length=100, blank=True,null=True)
    qc_worker = models.ForeignKey('UserProfile', on_delete=models.CASCADE,related_name='qc_worker',null=True)
    resume_worker_status = models.TextField(max_length=500, blank=True)
    qc_wroker_status = models.TextField(max_length=500, blank=True)
    status = models.TextField(max_length=500, blank=True)
    rejected = models.IntegerField(default = 0)