# typeidea/urls.py
from django.contrib import admin
from django.urls import path

from typeidea.custom_site import custom_site

urlpatterns = [
    path('super_admin/', admin.site.urls, name='super-admin'),
    path('admin/', custom_site.urls, name='admin'),
]

