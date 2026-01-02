"""
URL configuration for alsovinted project.

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
from client import views as client_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', client_views.home, name="home"),
    path('client/get_clothes/', client_views.get_vinted_articles, name="get_clothes"),
    path('client/save_preset/', client_views.save_preset, name="save_preset"),
    path('client/load_preset/', client_views.load_preset, name="load_preset"),
    path('client/setup_session/', client_views.setup_session, name="setup_session"),
]
