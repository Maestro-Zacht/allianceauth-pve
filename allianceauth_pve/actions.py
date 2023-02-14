from django.db.models import Sum, Subquery
from django.db.models.functions import Coalesce
from django.utils import timezone

from .models import EntryCharacter, Rotation
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

    if result.exists():
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
                    errors.append('Form not valid, you need at least 1 person to receive loot')
            else:
                errors.append('Not enough shares or roles')
        else:
            errors.append('Entry form or shares are not correct')
    else:
        errors.append('Error in roles')

    return errors
