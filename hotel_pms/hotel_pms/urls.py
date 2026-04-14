from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('reservations.urls')),
    path('rooms/', include('rooms.urls')),
    path('guests/', include('guests.urls')),
    path('billing/', include('billing.urls')),
    path('staff/', include('staff.urls')),
    path('ota/', include('ota.urls')),
]
