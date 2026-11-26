from datetime import timedelta

from django.conf import settings
from django.utils import timezone


def site_links(request):
    return {
        "erp_test_installer_url": getattr(settings, "ERP_TEST_INSTALLER_URL", ""),
        "google_analytics_id": getattr(settings, "GOOGLE_ANALYTICS_ID", ""),
        "whatsapp_url": getattr(settings, "WHATSAPP_URL", ""),
    }


def admin_site_analytics(request):
    if request.path != "/admin/" or not request.user.is_active or not request.user.is_staff:
        return {}

    from .models import SiteVisit

    today = timezone.localdate()
    visits_today = SiteVisit.objects.filter(visited_at__date=today)
    visitors_30_days = SiteVisit.objects.filter(
        visited_at__gte=timezone.now() - timedelta(days=30)
    )
    return {
        "site_visitors_today": visits_today.values("visitor_id").distinct().count(),
        "site_pageviews_today": visits_today.count(),
        "site_visitors_30_days": visitors_30_days.values("visitor_id").distinct().count(),
    }
