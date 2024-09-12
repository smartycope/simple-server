"""
URL configuration for simple_server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from simple_page import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('submit/', views.submit, name='submit'),
    path('key/', views.key, name='key'),
    path('arrow/<str:key>/', views.arrow, name='arrow'),
    path('playpause/', views.playpause, name='playpause'),
    path('temp/', views.temp_graph, name='temp'),
    path('temp2/', views.temp_graph2, name='temp2'),
    # path('volume/<int:add>/', views.change_volume, name='volume')
]
