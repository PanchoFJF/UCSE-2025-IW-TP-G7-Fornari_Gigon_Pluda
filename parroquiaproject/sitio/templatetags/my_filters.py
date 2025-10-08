from django import template
from django.utils.timesince import timesince

register = template.Library()

@register.filter
def timesince_one(value):
    if not value:
        return ""
    delta = timesince(value)
    return delta.split(",")[0]

@register.filter(name='add_class')
def add_class(field, css):
    return field.as_widget(attrs={"class": css})

@register.filter
def to(value, arg):
    """Itera de 1 a arg inclusive"""
    return range(value, arg + 1)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)