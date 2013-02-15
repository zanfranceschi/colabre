from django import template

register = template.Library()

@register.filter
def newline_to_br(value):
    return value.replace("\n", "<br />")
