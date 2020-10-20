# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from app.models import UserProfile
import json

@login_required(login_url="/login/")
def index(request):
    
    context = {}
    context['segment'] = 'index'

    html_template = loader.get_template( 'index.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def pages(request):
    
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        
        load_template      = request.path.split('/')[-1]
        context['segment'] = load_template
        
        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))
        
    except template.TemplateDoesNotExist:

        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))

    except:
    
        html_template = loader.get_template( 'page-500.html' )
        return HttpResponse(html_template.render(context, request))


@require_http_methods(["GET", "POST"])
def userinfo(request,data=None):
    
    user = UserProfile.objects.filter(id =  request.user.id).first()
    
        
    if request.POST.get("email") is not None:
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        user.first_name = name
        user.phone = phone
        user.address = address
        user.save()
    
    data = {}
    data["email"] = user.email
    if user.phone is None:
        data["phone"] = ""
    else:
        data["phone"] = user.phone
    data["name"] = user.first_name + " " +  user.last_name
    data["role"] = user.role
    if user.address is None:
        data["address"] = ""
    else:
        data["address"] = user.address
    
    return HttpResponse( json.dumps( data ) )
   


