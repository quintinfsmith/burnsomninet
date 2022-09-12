"""burnsomninet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404, handler500
from django.conf import settings
import os

from burnsomninet import views

SITECODE = settings.SITECODE

urlpatterns = [
    path("", views.index, name="index"),
    path("javascript/<path:file_path>", views.javascript_controller),
    path("style/<str:style_name>.css", views.style, name="style"),
    path("keybase.txt", views.keybase, name="keybase"),
    path("favicon.ico", views.favicon, name="favicon"),
    #path("ntest/",  include('ntest.urls')),
    path('admin/', admin.site.urls),
    path("content/<path:content_path>", views.content_controller),
    path('api/<path:section_path>', views.api_controller),
    path("<str:section>/<path:subsection_path>", views.section_controller),
    path("<str:section>/<str:subsection>.json", views.section_json),
]


handler404 = views.handler404
#handler404 = 'views.handle404'
handler500 = views.handler500
