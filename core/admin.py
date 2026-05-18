from django.contrib import admin

from .models import CRMAccessRequest, EmpresaReceita, Inscricao


@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "empresa", "cargo", "data_inscricao")
    search_fields = ("nome", "email", "empresa", "cargo", "mensagem")
    list_filter = ("data_inscricao",)


@admin.register(EmpresaReceita)
class EmpresaReceitaAdmin(admin.ModelAdmin):
    list_display = (
        "razao_social",
        "cnpj",
        "uf",
        "municipio",
        "cnae_principal",
        "data_abertura",
        "enrichment_status",
    )
    search_fields = ("razao_social", "nome_fantasia", "cnpj", "email", "telefone")
    list_filter = ("uf", "situacao_cadastral", "enrichment_status", "data_abertura")


@admin.register(CRMAccessRequest)
class CRMAccessRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "empresa", "telefone", "status", "created_at")
    search_fields = ("user__email", "user__first_name", "empresa", "telefone")
    list_filter = ("status", "created_at")
