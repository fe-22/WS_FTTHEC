from django.conf import settings


def site_links(request):
    return {
        "erp_test_installer_url": getattr(settings, "ERP_TEST_INSTALLER_URL", ""),
    }
