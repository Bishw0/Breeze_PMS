from django.urls import path

from ota.views import inbox_view, ingest_view


urlpatterns = [
    path("", inbox_view, name="ota_inbox"),
    path("ingest/", ingest_view, name="ota_ingest"),
]
