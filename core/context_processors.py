from django.conf import settings


def site_links(request):
    return {
        "erp_test_installer_url": getattr(settings, "ERP_TEST_INSTALLER_URL", ""),
        "google_analytics_id": getattr(settings, "GOOGLE_ANALYTICS_ID", ""),
        "whatsapp_url": getattr(settings, "WHATSAPP_URL", ""),
    }
