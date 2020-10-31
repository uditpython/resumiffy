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
from background_task import background
from datetime import timedelta
import os
from django.conf import settings 
from django.core.mail import send_mail

from django.core.mail import EmailMessage



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

@background(schedule=60)
def notify_order(order_numeber,package,first_name):
   
    order_info = OrderInfo.objects.filter(order_id= order_numeber,package = package).first()
    
    if order_info.worker_upload == 0:
    # lookup user by id and send them a message
        subject = 'Order Not fulfilled'
        message = f'Hi , Resume not submitted since last 24 hours for order number ' + order_numeber + " for package " + package + "." +  first_name + " is working on it."
        message = ' '.join(message.split())
        email_from = settings.EMAIL_HOST_USER 
        recipient_list = ["uditmital86@gmail.com", ] 
        send_mail( subject, message, email_from, recipient_list ) 

@background(schedule=60)
def notify_qc(order_numeber,package):
   
    order_info = OrderInfo.objects.filter(order_id= order_numeber,package = package).first()
    
    if order_info.qc_upload == 0:
    # lookup user by id and send them a message
        subject = 'QC not Done'
        message = f'Hi , QC not done for resume since last 24 hours for order number ' + order_numeber + " for package " + package + "."
        message = ' '.join(message.split())
        email_from = settings.EMAIL_HOST_USER 
        recipient_list = ["uditmital86@gmail.com", ] 
        send_mail( subject, message, email_from, recipient_list ) 

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
    order_det = json.loads(request.POST.get('data'))
    order_info = OrderInfo.objects.filter(order_id= order_det["order_number"],package = order_det["product"]).first()
    
    order_info.worker_upload += 1
    order_info.new_resume_url = url
    order_info.filename = name
    order_info.resume_status = "QC pending"
    order_info.resume_worker_status = "QC pending"
    order_info.save()
    notify_qc(order_info.order_id,order_info.package,schedule=timedelta(minutes=24*60))
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
    data = None
    while data is None:
        data = wcapi.get("orders")
      
    data = json.loads(data.text)
    final_result = []
    
    order_info = OrderInfo.objects.all()
    
    order_dict = {}

    for i in order_info:
        order_dict[i.order_id+"-" + i.package] = i
        
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
            # if result["order_number"] == '2093':
            #     import pdb
            #     pdb.set_trace()
            worker = result["order_number"] + "-" + result["product"]
            if worker in order_dict:
                
                if  order_dict[worker].resume_worker_status == "assigned":
                    
                    if order_dict[worker].resume_worker.id == request.user.id:
                        result["status"] = 'started'
                    else:
                        result["status"] = 'Another worker is working on'
                    result["resume_status"] = "work has started"
                    
                   
                else:
                   
                    if order_dict[worker].status == 'qc worker assigned':
                        
                        if order_dict[worker].qc_worker.id == request.user.id:
                            result["status"] = 'started'
                        else:
                            result["status"] = 'QC worker is working on' 
                    else:
                        if order_dict[worker].resume_worker.id == request.user.id:
                            result["status"] = 'started'
                        else:
                            result["status"] = 'Another worker is working on'
                    result["resume_status"] = order_dict[worker].resume_worker_status
                    
                if order_dict[worker].new_resume_url == None:
                    result["resume_new_url"] = ''
                else:
                    result["resume_new_url"] = order_dict[worker].new_resume_url
                result["number_rejected"] = order_dict[worker].rejected
            else:
                result["status"] = 'not started'
                result["resume_status"] = "Work has not started"
                result["resume_new_url"] = ''
                result["number_rejected"] = ''
            if  result["resume_status"] == "APPROVED":
                result["status"] = "DELIVERED"
            if result["resume_new_url"] != '' and  result["resume_status"] == 'QC pending':
                if order_dict[worker].resume_worker.id == request.user.id:
                    result['qc_check'] = "You are working on Resume So Can't Do QC Check "
                else:
                    result['qc_check'] = "PENDING"
            else:
                
                if result["resume_status"] == "APPROVED":
                     result['qc_check'] = 'APPROVED'
                else:
                    result['qc_check'] = ''
            
            if result["status"] == "DELIVERED":
                result["final_status"] = result["status"] 
            elif  result["resume_status"] == "Work has not started":
                result["final_status"] = "WORK HAS NOT STARTED"
            elif result["resume_status"] == 'QC pending':
                result["final_status"] = "QC pending"
            else:
                result["final_status"] = "IN PROGRESS"
            if  result["resume_status"] == 'QC_REJECTED':
                result["rejection_reason"] =  order_dict[worker].rejection_reason
            else:
                result["rejection_reason"] = ''
                
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

@background(schedule=60)
def send_delivery(id):

    email_from = settings.EMAIL_HOST_USER 
    order_det = OrderInfo.objects.filter(id=id).first()
    
    recipient_list = [order_det.email, ] 
    email = EmailMessage(
            'Resume is Ready', 'Here is your attached Resume.', settings.EMAIL_HOST_USER, recipient_list)
    email.attach_file(order_det.filename)
    email.send()

@require_http_methods(["GET", "POST"])

def qc_status(request):
    
    if request.POST.get('status') == "approve":
        order_numeber = request.POST['url[order_number]']
        package = request.POST['url[product]']
        order_det = OrderInfo.objects.filter(order_id=order_numeber,package=package).first()
        
        order_det.qc_worker = UserProfile.objects.get(id = request.user.id)
        order_det.status= "APPROVED"
        order_det.resume_worker_status = "APPROVED"
        order_det.qc_upload += 1
        send_delivery(order_det.id)
        order_det.save()


    elif request.POST.get('status') == "reject":
       
        order_numeber = request.POST['url[order_number]']
        package = request.POST['url[product]']
        order_det = OrderInfo.objects.filter(order_id=order_numeber,package=package).first()
        order_det.qc_worker = UserProfile.objects.get(id = request.user.id)
        order_det.resume_worker_status = "QC_REJECTED"
        order_det.rejected += 1
        order_det.qc_upload += 1
        order_det.rejection_reason = request.POST['reason']
        if request.POST['performer'] != 'qc':
            order_det.status = "resume worker assigned" 
            order_det.save()
            user = UserProfile.objects.filter(id =  order_det.resume_worker.id).first()
            if order_det.rejected > 1:
                subject = 'Resume Got Rejected'
                message = f'Hi , QC has rejected Resume for Order Number' + order_numeber + " for package " + package + "." +  user.first_name + " is working on it."
                message = ' '.join(message.split())
                email_from = settings.EMAIL_HOST_USER 
                recipient_list = ["uditmital86@gmail.com", ] 
                send_mail( subject, message, email_from, recipient_list ) 
        else:
            
            order_det.status = 'qc worker assigned'
            order_det.save()
            
    data = {"staus":"done"}
    return HttpResponse( json.dumps( data ) )

    
@require_http_methods(["GET", "POST"])
@login_required(login_url="/login/")
def assign_worker(request):
    
    user_id = UserProfile.objects.get(id = request.user.id)
    order_cnt = OrderInfo.objects.filter(resume_worker = UserProfile.objects.get(id = request.user.id)).exclude(status = 'APPROVED').count()
    if order_cnt > 3:
        data = {"status":"exceeded"}
        return HttpResponse( json.dumps( data ) )
    new_order= OrderInfo()
    new_order.order_id = request.POST['url[order_number]']
    new_order.package = request.POST['url[product]']
    new_order.email = request.POST['url[email]']

    new_order.resume_url = request.POST['url[uploaded_resume]']
    new_order.resume_worker_status = "assigned"
    new_order.status = "resume worker assigned" 
    new_order.resume_worker = user_id
   
    new_order.save()
    notify_order(new_order.order_id,new_order.package,new_order.resume_worker.first_name,schedule=timedelta(minutes=24*60))
    
    data = {"status":"done"}
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
   

