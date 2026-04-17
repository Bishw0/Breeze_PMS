from django.urls import path

from reservations import views


urlpatterns = [
    path("", views.pricing_rule_list, name="pricing_rule_list"),
    path("create/", views.pricing_rule_create, name="pricing_rule_create"),
]
