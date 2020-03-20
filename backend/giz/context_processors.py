from django.conf import settings

def resource_urls(request):
    default = dict(
        SITE_NAME = getattr(settings, 'SITE_NAME'),
    )
    return default