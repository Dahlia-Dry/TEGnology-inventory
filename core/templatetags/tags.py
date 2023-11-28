from django import template

register = template.Library()

@register.filter
def get_attr(obj, attr):
    return getattr(obj, attr.lower())

@register.filter
def key(obj, key):
    return obj[key]

@register.filter
def as_title(obj):
    return str.title(obj.replace('_',' '))