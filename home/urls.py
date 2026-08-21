from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/power/', views.power_api, name='power_api'),
    path('login/', views.login_view, name='login'),
    path('resister/', views.resister, name='resister'),
]
