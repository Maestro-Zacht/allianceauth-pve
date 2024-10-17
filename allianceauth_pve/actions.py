from django.db.models import Sum, Subquery
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.translation import gettext as _

from .models import EntryCharacter, Rotation, RotationPreset
from .forms import NewEntryForm, NewShareFormSet, NewRoleFormSet


def running_averages(user, start_date, end_date=None):
    if end_date is None:
        end_date = timezone.now()

    rotations = Rotation.objects.filter(closed_at__range=(start_date, end_date)).get_setup_summary().filter(user=user).values('total_setups')
    result = (
        EntryCharacter.objects
        .filter(entry__rotation__closed_at__range=(start_date, end_date), user=user)
        .with_totals()
        .values('user').order_by()
        .annotate(helped_setups=Coalesce(Subquery(rotations[:1]), 0))
        .annotate(estimated_total=Sum('estimated_share_total'))
        .annotate(actual_total=Sum('actual_share_total'))
        .values(
            'helped_setups',
            'estimated_total',
            'actual_total'
        )
    )

    if result:
        return result[0]
    else:
        return {}


def check_forms_valid(role_form: NewRoleFormSet, entry_form: NewEntryForm, share_form: NewShareFormSet) -> list:
    errors = []

    if role_form.is_valid():
        roles_choices = []
        roles_values = {}
        for new_role in role_form.cleaned_data:
            roles_choices.append((new_role['name'], new_role['name']))
            roles_values[new_role['name']] = new_role['value']

        for form in share_form:
            form.fields['role'].choices = roles_choices

        if entry_form.is_valid() and share_form.is_valid():
            if share_form.total_form_count() > 0 and role_form.total_form_count() > 0:
                total_value = 0
                for share in share_form.cleaned_data:
                    total_value += share['site_count'] * roles_values[share['role']]

                if total_value == 0:
                    errors.append(_('Form not valid, you need at least 1 person to receive loot'))
            else:
                errors.append(_('Not enough shares or roles'))
        else:
            errors.append(_('Entry form or shares are not correct'))
    else:
        errors.append(_('Error in roles'))

    return errors


def ensure_rotation_presets_applied():
    missing_setups = RotationPreset.objects.exclude(
        name__in=Rotation.objects.filter(is_closed=False).values('name')
    )

    for setup in missing_setups:
        r = Rotation.objects.create(
            name=setup.name,
            max_daily_setups=setup.max_daily_setups,
            min_people_share_setup=setup.min_people_share_setup,
            tax_rate=setup.tax_rate,
            priority=setup.priority,
        )

        r.entry_buttons.set(setup.entry_buttons.all())
        r.roles_setups.set(setup.roles_setups.all())
