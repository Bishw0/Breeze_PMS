from django.contrib import admin
from .models import StaffProfile, ShiftLog

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'employee_id', 'is_active']

admin.site.register(ShiftLog)
