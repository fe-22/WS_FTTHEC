from django.urls import path

from .views import (
    crm_view,
    dashboard_demo,
    financeiro_demo,
    home,
    inscricao_view,
    operacoes_demo,
    pdv_demo,
)

urlpatterns = [
    path('', home, name='home'),
    path('inscricao/', inscricao_view, name='inscricao'),
    path('crm/', crm_view, name='crm'),
    path('demo/dashboard/', dashboard_demo, name='dashboard_demo'),
    path('demo/financeiro/', financeiro_demo, name='financeiro_demo'),
    path('demo/operacoes/', operacoes_demo, name='operacoes_demo'),
    path('demo/pdv/', pdv_demo, name='pdv_demo'),
]
