from django.urls import path

from .views import (
    crm_empresa_enriquecer_api,
    crm_invite_create_view,
    crm_register_invite_view,
    crm_empresas_api,
    crm_view,
    crm_register_view,
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
    path('accounts/register/', crm_register_view, name='crm_register'),
    path('accounts/invite/', crm_invite_create_view, name='crm_invite_create'),
    path(
        'accounts/register/invite/<str:token>/',
        crm_register_invite_view,
        name='crm_register_invite',
    ),
    path('crm/', crm_view, name='crm'),
    path('crm/api/empresas/', crm_empresas_api, name='crm_empresas_api'),
    path(
        'crm/api/empresas/<int:empresa_id>/enriquecer/',
        crm_empresa_enriquecer_api,
        name='crm_empresa_enriquecer_api',
    ),
    path('demo/dashboard/', dashboard_demo, name='dashboard_demo'),
    path('demo/financeiro/', financeiro_demo, name='financeiro_demo'),
    path('demo/operacoes/', operacoes_demo, name='operacoes_demo'),
    path('demo/pdv/', pdv_demo, name='pdv_demo'),
]
