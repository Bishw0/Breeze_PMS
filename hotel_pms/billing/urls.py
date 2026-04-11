from django.urls import path
from . import views

urlpatterns = [
    path('', views.invoice_list, name='invoice_list'),
    path('<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('<int:pk>/pay/', views.add_payment, name='add_payment'),
    path('reports/revenue/', views.revenue_report, name='revenue_report'),
]
