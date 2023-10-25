from typing import Dict

from django.http import HttpRequest

from site_settings.models import SiteSettings


def site_settings(request: HttpRequest) -> Dict[str, SiteSettings]:
    settings = SiteSettings.load()
    request.site_settings = settings
    return {"site_settings": settings}
