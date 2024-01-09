from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.home , name='home'),
    path('login', views.login_view , name='login'),
    path('logout', views.logout_view , name='logout'),
    path('register', views.register , name='register'),
    path('active/<uid64>/<token>', views.activate_view , name='active'),
]
