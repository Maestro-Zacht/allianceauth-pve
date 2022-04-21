from django import template
from django.contrib.auth.models import User


register = template.Library()


@register.filter
def get_main_character(eve_obj, attr: str = None):
    if isinstance(eve_obj, User):
        if attr:
            return getattr(eve_obj.profile.main_character, attr)
        else:
            return eve_obj.profile.main_character
    elif isinstance(eve_obj, int):
        try:
            if attr:
                return getattr(User.objects.get(pk=eve_obj).profile.main_character, attr)
            else:
                return User.objects.get(pk=eve_obj).profile.main_character
        except:
            return ''
    else:
        return ''
