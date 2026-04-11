from django.contrib import admin
from .models import Room, RoomType, MaintenanceRequest

@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_price', 'capacity']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['number', 'room_type', 'floor', 'status', 'current_price']
    list_filter = ['status', 'floor', 'room_type']

@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ['room', 'title', 'priority', 'status', 'created_at']
    list_filter = ['status', 'priority']
