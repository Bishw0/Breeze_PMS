from django.contrib import admin
from .models import Guest

@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'vip_status', 'total_stays']
    search_fields = ['first_name', 'last_name', 'email']
    list_filter = ['vip_status', 'nationality']
