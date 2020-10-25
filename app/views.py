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
from app.models import UserProfile,OrderInfo
import json
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from woocommerce import API
from django.views.static import serve

import os
coll = {}
coll["field_5f3555c914f44"] = "name"
coll["field_5f3555f214f45"] = "dob"
coll["field_5f35561514f46"] = "email"
coll["field_5f35565514f48"] = "profession"
coll["field_5f35562014f47"] = "phone"
coll["field_5f3559335fa91"] = "tell_us_about_yourself"
coll["field_5f35525e40fc8"] = "edu_details"
coll["field_5f3554f614f3b"] = "education"
coll["field_5f3552c240fc9"] = "year"
coll["field_5f35547214f36"] = "subject"
coll["field_5f35548e14f37"] = "marks_percentage"
coll["field_5f35549a14f38"] = "any_notable_achievements"
coll["field_5f3554c614f39"] = "club_activities"

coll["field_5f3554cb14f3a"] = "social_activities"
coll["field_5f35552f14f3c"] = "work_experience"
coll["field_5f35554d14f3d"] = "company_"
coll["field_5f35555614f3e"] = "work_year"
coll["field_5f35555b14f3f"] = "role__position"
coll["field_5f35556a14f40"] = "specific_projects_"
coll["field_5f35557c14f41"] = "achievements"
coll["field_5f35559214f42"] = "tech_projects"







wcapi = API(
    url="https://resumifyy.com",
    consumer_key="ck_f2baac93e1325ae22adc808f964f6fd663aa5874",
    consumer_secret="cs_784847f6211887c0b0ae43a43d66e49cec675f53",
    version="wc/v3"
)

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


@login_required(login_url="/login/")
@require_http_methods(["GET", "POST"])
@csrf_exempt
def upload_resume(request):
    uploaded_file = request.FILES['myfile']
    fs = FileSystemStorage()
    name = fs.save(uploaded_file.name, uploaded_file)
    url = fs.url(name)
    url = "/view_image/"+url
    import pdb; pdb.set_trace()
    data = {"staus":"done"}
    return HttpResponse( json.dumps( data ) )

@login_required(login_url="/login/")
@require_http_methods(["GET", "POST"])
@csrf_exempt
def view_image(request,filepath):
#    filepath = "file_UFTs8qD.pdf"
   return serve(request, os.path.basename(filepath), os.path.dirname(filepath))
   

@require_http_methods(["GET", "POST"])
def orders_view(request):
    data = wcapi.get("orders")
    data = json.loads(data.text)
    final_result = []
    
    order_info = OrderInfo.objects.all()
    order_dict = {}

    for i in order_info:
        order_dict[i.order_id] = i
    for i in data:
        
        for j in i["line_items"]:
            result = {}
            result["order_number"] = i["number"]
            result["product"] = j["name"]
            result["email"] =  i["billing"]["email"]
            if  i["meta_data"][1]["key"] == "existing_resume":
                result["uploaded_resume"] = i["meta_data"][1]["value"]
            else:
                result["uploaded_resume"] = ''
                
            if  i["meta_data"][2]["key"] == "existing_res":
                result["uploaded_image"] = i["meta_data"][2]["value"]
            else:
                result["uploaded_image"] = ''
            result["order_details"] = "/orders/"+result["order_number"]
            
            if result["order_number"] in order_dict and  result["product"] == order_dict[result["order_number"]].package:
               
                if  order_dict[result["order_number"]].resume_worker_status == "assigned":
                
                    result["status"] = 'started'
                else:
                    result["status"] = 'submitted'
                
            else:
                result["status"] = 'not started'
            
            final_result.append(result)
    return render(request, "index.html", {"data": json.dumps(final_result)})

@require_http_methods(["GET", "POST"])
def user_profile_view(request,user_id):
    data = wcapi.get("orders/"+str(user_id))
    data = json.loads(data.text)
    result = {}
    result["customer_note"] = data["customer_note"]
    
    if  data["meta_data"][3]["key"] == "data":
        new_data = data["meta_data"][3]["value"]
        for i in new_data:
            try:
                
                result[coll[i]] =  new_data[i]

            except:
                pass

        edu = []
        if 'edu_details' in result:
            for i in result["edu_details"]:
                edu_det = {}
                for keys in result["edu_details"][i]:
                    
                    edu_det[coll[keys]] = result["edu_details"][i][keys]
                edu.append(edu_det)
            
        result["edu_details"] = edu   
         


        work = []
        if 'work_experience' in result:

            for i in result["work_experience"]:
                work_det = {}
                for keys in result["work_experience"][i]:
                    
                    work_det[coll[keys]] = result["work_experience"][i][keys]
                work.append(work_det)
        
        result["work_experience"] = work
        if 'dob' in result:
            
            result['dob'] =   result['dob'][-2:]+"/" + result['dob'][-4:-2]+"/"+result['dob'][:-4]
        if 'name'not in result:
            result['name'] = data['billing']["first_name"] +  " " +    data['billing']["last_name"]
            result["email"] = data["billing"]["email"]    
            result["phone"] = data["billing"]["phone"]
            result["dob"] = ''
            result["profession"] = ''
            result['tell_us_about_yourself'] = ''
    return render(request, "order_details.html", {"data": json.dumps(result)})

@require_http_methods(["GET", "POST"])
@login_required(login_url="/login/")
def assign_worker(request):
    

    try:
        new_order= OrderInfo()
        new_order.order_id = request.POST['url[order_number]']
        new_order.package = request.POST['url[product]']
        new_order.email = request.POST['url[email]']
    
        new_order.resume_url = request.POST['url[uploaded_resume]']
        new_order.resume_worker_status = "assigned"
        new_order.status = "resume worker assigned" 
        new_order.resume_worker = UserProfile.objects.get(id = request.user.id)
        new_order.save()
    except:
        pass

    data = {"staus":"done"}
    return HttpResponse( json.dumps( data ) )


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
   

