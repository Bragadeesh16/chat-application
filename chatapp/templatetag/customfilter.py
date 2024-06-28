from django import template

register = template.library()

@register.filter
def if_id_in_queryset(id,queryset):
    pass