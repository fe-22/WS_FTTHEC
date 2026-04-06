from django.urls import path
from .views import home, inscricao_view, crm_view, dashboard_demo, pdv_demo

urlpatterns = [
    path('', home, name='home'),
    path('inscricao/', inscricao_view, name='inscricao'),
    path('crm/', crm_view, name='crm'),
    path('demo/dashboard/', dashboard_demo, name='dashboard_demo'),
    path('demo/pdv/', pdv_demo, name='pdv_demo'),
]