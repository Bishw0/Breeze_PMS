from django.contrib import admin
from .models import Reservation, ServiceCharge, RoomServiceItem

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['reservation_number', 'guest', 'room', 'check_in', 'check_out', 'status']
    list_filter = ['status', 'source']
    search_fields = ['reservation_number', 'guest__first_name', 'guest__last_name']

admin.site.register(RoomServiceItem)
admin.site.register(ServiceCharge)
