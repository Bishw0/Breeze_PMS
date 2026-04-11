from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.staff_login, name='staff_login'),
    path('logout/', views.staff_logout, name='staff_logout'),
    path('', views.staff_list, name='staff_list'),
    path('new/', views.staff_create, name='staff_create'),
    path('profile/', views.my_profile, name='my_profile'),
]
