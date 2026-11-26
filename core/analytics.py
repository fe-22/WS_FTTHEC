import uuid
from django.utils import timezone


TRACKING_COOKIE = "fthec_visitor"


def get_client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def get_location(request):
    country = (
        request.META.get("HTTP_CF_IPCOUNTRY")
        or request.META.get("HTTP_X_COUNTRY")
        or request.META.get("HTTP_X_VERCEL_IP_COUNTRY")
        or ""
    ).upper()
    region = (
        request.META.get("HTTP_CF_REGION")
        or request.META.get("HTTP_X_REGION")
        or request.META.get("HTTP_X_VERCEL_IP_COUNTRY_REGION")
        or ""
    )
    city = (
        request.META.get("HTTP_CF_IPCITY")
        or request.META.get("HTTP_X_CITY")
        or request.META.get("HTTP_X_VERCEL_IP_CITY")
        or ""
    )
    return country, region, city


class SiteAnalyticsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.method != "GET":
            return response
        if request.path.startswith("/admin") or request.path.startswith("/static/"):
            return response

        from .models import SiteVisit

        visitor_id = request.COOKIES.get(TRACKING_COOKIE)
        is_new_cookie = not visitor_id
        if is_new_cookie:
            visitor_id = uuid.uuid4().hex

        today = timezone.localdate()
        already_recorded = SiteVisit.objects.filter(
            visitor_id=visitor_id,
            path=request.path,
            visited_at__date=today,
        ).exists()

        if not already_recorded:
            country, region, city = get_location(request)
            SiteVisit.objects.create(
                visitor_id=visitor_id,
                ip_address=get_client_ip(request)[:45],
                path=request.path[:500],
                referrer=request.META.get("HTTP_REFERER", "")[:500],
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
                country=country[:10],
                region=region[:100],
                city=city[:100],
            )

        if is_new_cookie:
            response.set_cookie(
                TRACKING_COOKIE,
                visitor_id,
                max_age=60 * 60 * 24 * 365,
                httponly=True,
                samesite="Lax",
            )
        return response
