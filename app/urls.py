# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from app import views

urlpatterns = [
    # Matches any html file - to be used for gentella
    # Avoid using your .html in your resources.
    # Or create a separate django app.
    re_path(r'^.*\.html', views.pages, name='pages'),

    # The home page
    path('', views.index, name='home'),
    path('orders/<int:user_id>/', views.user_profile_view),
    path('ordersinfo/', views.orders_view),
    path('assign_worker/', views.assign_worker),
    path('upload_resume/',views.upload_resume),
    path('userinfo/', views.userinfo, name="userinfo"),
    path('view_image/<str:filepath>',views.view_image),
    
]
