from django import template
from django.contrib.auth.models import User

from allianceauth.eveonline.models import EveCharacter


register = template.Library()


@register.filter
def get_main_character(eve_obj):
    if isinstance(eve_obj, str):
        try:
            eve_obj = int(eve_obj)
        except:
            return ''

    if isinstance(eve_obj, User):
        return eve_obj.profile.main_character
    elif isinstance(eve_obj, int):
        try:
            return User.objects.get(pk=eve_obj).profile.main_character
        except:
            return ''
    else:
        return ''


@register.filter
def get_char_attr(character_obj, attr: str):
    if isinstance(character_obj, str):
        try:
            character_obj = int(character_obj)
        except:
            return ''

    if isinstance(character_obj, EveCharacter):
        return getattr(character_obj, attr)
    elif isinstance(character_obj, int):
        try:
            return getattr(EveCharacter.objects.get(pk=character_obj), attr)
        except:
            return ''
    else:
        return ''
