from django.contrib import admin
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta

from .models import CRMAccessRequest, EmpresaReceita, Inscricao, SiteVisit


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


@admin.register(SiteVisit)
class SiteVisitAdmin(admin.ModelAdmin):
    change_list_template = "admin/core/sitevisit/change_list.html"
    list_display = (
        "visited_at",
        "path",
        "city",
        "region",
        "country",
        "referrer",
    )
    list_filter = ("visited_at", "country", "region", "city")
    search_fields = ("path", "city", "region", "country", "referrer", "visitor_id")
    readonly_fields = (
        "visitor_id",
        "ip_address",
        "path",
        "referrer",
        "user_agent",
        "country",
        "region",
        "city",
        "visited_at",
    )
    date_hierarchy = "visited_at"

    def changelist_view(self, request, extra_context=None):
        now = timezone.now()
        today = timezone.localdate()
        last_30_days = now - timedelta(days=30)
        queryset = SiteVisit.objects.all()

        visits_today = queryset.filter(visited_at__date=today).count()
        visitors_today = queryset.filter(visited_at__date=today).values("visitor_id").distinct().count()
        visitors_30_days = queryset.filter(visited_at__gte=last_30_days).values("visitor_id").distinct().count()
        top_pages = list(
            queryset.values("path").annotate(total=Count("id")).order_by("-total")[:8]
        )
        top_regions = list(
            queryset.exclude(region="")
            .values("region")
            .annotate(total=Count("visitor_id", distinct=True))
            .order_by("-total")[:8]
        )
        top_cities = list(
            queryset.exclude(city="")
            .values("city", "region")
            .annotate(total=Count("visitor_id", distinct=True))
            .order_by("-total")[:8]
        )
        top_referrers = list(
            queryset.exclude(referrer="")
            .values("referrer")
            .annotate(total=Count("visitor_id", distinct=True))
            .order_by("-total")[:8]
        )
        daily = list(
            queryset.filter(visited_at__gte=last_30_days)
            .annotate(day=TruncDate("visited_at"))
            .values("day")
            .annotate(visitors=Count("visitor_id", distinct=True))
            .order_by("day")
        )

        extra_context = extra_context or {}
        extra_context.update({
            "analytics": {
                "visits_today": visits_today,
                "visitors_today": visitors_today,
                "visitors_30_days": visitors_30_days,
                "top_pages": top_pages,
                "top_regions": top_regions,
                "top_cities": top_cities,
                "top_referrers": top_referrers,
                "daily": daily,
            }
        })
        return super().changelist_view(request, extra_context=extra_context)
