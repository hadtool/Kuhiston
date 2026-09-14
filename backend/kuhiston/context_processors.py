from django.conf import settings

from . import brand


def brand_context_processor(request):
    lang = getattr(request, "LANGUAGE_CODE", settings.LANGUAGE_CODE)
    return {
        "brand_name": brand.APP_NAME,
        "brand_tagline": brand.APP_TAGLINE.get(lang, brand.APP_TAGLINE.get("en", "")),
    }