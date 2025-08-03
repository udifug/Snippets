from django import template
from MainApp.models import LANG_ICONS

register = template.Library()

def get_lang_icon(lang):
    return LANG_ICONS.get(lang)

def messages_type_mapping(value):
    mapping = {
        'error' : 'danger',
        'debug' : 'dark'
    }
    return mapping.get(value, value)

register.filter('get_lang_icon',get_lang_icon)
register.filter('messages_type_mapping', messages_type_mapping)