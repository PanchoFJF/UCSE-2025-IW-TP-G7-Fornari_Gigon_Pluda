from django import template
from django.utils.timesince import timesince

register = template.Library()

@register.filter
def timesince_one(value):
    if not value:
        return ""
    delta = timesince(value)
    return delta.split(",")[0]