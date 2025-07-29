from django import template
from MainApp.models import LANG_ICONS

register = template.Library()

def get_lang_icon(lang):
    return LANG_ICONS.get(lang)

register.filter('get_lang_icon',get_lang_icon)