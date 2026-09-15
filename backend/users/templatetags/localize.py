from django import template

register = template.Library()


@register.filter
def get_name(obj, lang):
    """Имя объекта на языке lang (метод get_name на модели)."""
    if hasattr(obj, "get_name"):
        return obj.get_name(lang)
    return str(obj)


@register.filter
def get_description(obj, lang):
    """Описание объекта на языке lang (метод get_description на модели)."""
    if hasattr(obj, "get_description"):
        return obj.get_description(lang)
    return ""