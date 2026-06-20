from django.conf import settings
from django.core.checks import Error, register

_ID = "allianceauth_pve"


def _check_setting_type(name, expected, *, id_suffix):
    """Return an Error if the setting is not of the expected type, else None."""
    value = getattr(settings, name)
    if not isinstance(value, expected):
        return Error(
            f"{name} must be {expected.__name__}, got {type(value).__name__}.",
            hint=f"Set {name} to a valid {expected.__name__} in your settings.",
            id=f"{_ID}.E{id_suffix}",
        )
    return None


def _check_setting_list_type(name, element_type, *, id_suffix):
    """Return an Error if the setting is not a list of element_type, else None."""
    value = getattr(settings, name)
    if not (
        isinstance(value, list) and all(isinstance(x, element_type) for x in value)
    ):
        return Error(
            f"{name} must be a list of {element_type.__name__}.",
            hint=f"e.g. {name} = [...]  # each item a {element_type.__name__}",
            id=f"{_ID}.E{id_suffix}",
        )
    return None


@register()
def check_settings(app_configs, **kwargs):  # noqa: ARG001
    errors = []

    if (
        hasattr(settings, "PVE_ONLY_MAINS")
        and (error := _check_setting_type("PVE_ONLY_MAINS", bool, id_suffix="001"))
        is not None
    ):
        errors.append(error)

    if (
        hasattr(settings, "PVE_IGNORED_ITEM_GROUPS")
        and (
            error := _check_setting_list_type(
                "PVE_IGNORED_ITEM_GROUPS", int, id_suffix="002"
            )
        )
        is not None
    ):
        errors.append(error)

    if (
        hasattr(settings, "PVE_IGNORED_ITEM_IDS")
        and (
            error := _check_setting_list_type(
                "PVE_IGNORED_ITEM_IDS", int, id_suffix="003"
            )
        )
        is not None
    ):
        errors.append(error)

    return errors
