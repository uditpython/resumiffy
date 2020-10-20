# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from app.models import UserProfile


# class MultiResumeField(forms.Field):
#     '''anyfunction'''
#     # def to_python(self, value):
#     #     """Normalize data to a list of strings."""
#     #     # Return an empty list if no input was given.
#     #     if not value:
#     #         return []
#     #     return value.split(',')

#     def validate(self, value):
#         """Check if value consists only of valid emails."""
#         # Use the parent's handling of required fields, etc.
#         super().validate(value)
        

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Username",                
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder" : "Password",                
                "class": "form-control"
            }
        ))

class SignUpForm(UserCreationForm):
    FRUIT_CHOICES= [
            ('', ''),
            ('Administrator', 'Administrator'),
            ('Resume Worker', 'Resume Worker'),
            ('Quality Controler', 'Quality Controller'),
            
            ]

    firstname = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "First name",                
                "class": "form-control"
            }
        ))

    lastname = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Last name",                
                "class": "form-control"
            }
        ))

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Username",                
                "class": "form-control"
            }
        ))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder" : "Email",                
                "class": "form-control"
            }
        ))
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder" : "Password",                
                "class": "form-control"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder" : "Password check",                
                "class": "form-control"
            }
        ))
    role= forms.CharField(label='What is your favorite fruit?', widget=forms.Select(choices=FRUIT_CHOICES,attrs = {'class':"dropdown-menu show",'style':"width: 100%;"}))

    class Meta:
        model = UserProfile
        fields = ('firstname','lastname','username', 'email', 'password1', 'password2','role')
