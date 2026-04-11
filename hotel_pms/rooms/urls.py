from django.urls import path
from . import views

urlpatterns = [
    path('', views.room_list, name='room_list'),
    path('<int:pk>/', views.room_detail, name='room_detail'),
    path('new/', views.room_create, name='room_create'),
    path('<int:pk>/edit/', views.room_edit, name='room_edit'),
    path('<int:pk>/status/', views.room_status_update, name='room_status_update'),
    path('maintenance/', views.maintenance_list, name='maintenance_list'),
    path('maintenance/new/', views.maintenance_create, name='maintenance_create'),
    path('maintenance/new/<int:room_pk>/', views.maintenance_create, name='maintenance_create_for_room'),
    path('maintenance/<int:pk>/edit/', views.maintenance_update, name='maintenance_update'),
]
