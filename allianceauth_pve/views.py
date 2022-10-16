import datetime
import re

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import F, Q, Count, Exists, OuterRef
from django.db import transaction
from django.views.generic.detail import DetailView
from django.conf import settings

from allianceauth.services.hooks import get_extension_logger
from allianceauth.authentication.models import CharacterOwnership

from .models import Entry, EntryCharacter, Rotation, EntryRole, General
from .forms import NewEntryForm, NewShareFormSet, NewRotationForm, CloseRotationForm, NewRoleFormSet
from .actions import running_averages, check_forms_valid

logger = get_extension_logger(__name__)


@login_required
@permission_required('allianceauth_pve.access_pve')
def index(request):
    return redirect('allianceauth_pve:dashboard')


@login_required
@permission_required('allianceauth_pve.access_pve')
def dashboard(request):
    open_rots = Rotation.objects.filter(is_closed=False).order_by('-priority')
    closed_rots = Rotation.objects.filter(is_closed=True).order_by('-closed_at')

    paginator_open = Paginator(open_rots, 10)
    paginator_closed = Paginator(closed_rots, 10)

    npage_open = request.GET.get('page_open')
    npage_closed = request.GET.get('page_closed')

    today = timezone.now().date()

    one_month_average = running_averages(request.user, today - datetime.timedelta(days=30))
    three_month_average = running_averages(request.user, today - datetime.timedelta(days=30 * 3))
    six_month_average = running_averages(request.user, today - datetime.timedelta(days=30 * 6))
    one_year_average = running_averages(request.user, today - datetime.timedelta(days=30 * 12))

    context = {
        'open_count': open_rots.count(),
        'open_rots': paginator_open.get_page(npage_open),
        'closed_rots': paginator_closed.get_page(npage_closed),
        'is_closed_param': npage_closed is not None,
        'onemonth': one_month_average,
        'threemonth': three_month_average,
        'sixmonth': six_month_average,
        'oneyear': one_year_average,
    }
    return render(request, 'allianceauth_pve/ratting-dashboard.html', context=context)


@login_required
@permission_required('allianceauth_pve.access_pve')
def rotation_view(request, rotation_id):
    r = get_object_or_404(Rotation, pk=rotation_id)

    if request.method == 'POST' and not r.is_closed and request.user.has_perm('allianceauth_pve.manage_rotations'):
        copied_data = request.POST.copy()
        copied_data['sales_value'] = copied_data['sales_value'].replace(',', '')
        closeform = CloseRotationForm(copied_data)

        if closeform.is_valid():
            with transaction.atomic():
                r.actual_total = closeform.cleaned_data['sales_value']
                r.is_closed = True
                r.closed_at = timezone.now()
                r.save()

            closeform = None
    elif not r.is_closed:
        closeform = CloseRotationForm()
    else:
        closeform = None

    summary = r.summary.order_by('-estimated_total').values(
        'user',
        'helped_setups',
        'estimated_total',
        'actual_total',
        character_name=F('user__profile__main_character__character_name'),
        character_id=F('user__profile__main_character__character_id'),
    )

    summary_count_half = summary.count() // 2

    entries_paginator = Paginator(r.entries.order_by('-created_at'), 10)
    page = request.GET.get('page')

    context = {
        'rotation': r,
        'summaries': [summary[:summary_count_half], summary[summary_count_half:]],
        'entries': entries_paginator.get_page(page),
        'closeform': closeform,
    }

    return render(request, 'allianceauth_pve/rotation.html', context=context)


@login_required
@permission_required('allianceauth_pve.manage_entries')
def get_avaiable_ratters(request, name=None):
    content_type = ContentType.objects.get_for_model(General)
    permission = Permission.objects.get(content_type=content_type, codename='access_pve')

    ownerships = CharacterOwnership.objects.filter(
        Q(user__groups__permissions=permission) |
        Q(user__user_permissions=permission) |
        Q(user__profile__state__permissions=permission),
        user__profile__main_character__isnull=False,
    )

    if name:
        alts_name = CharacterOwnership.objects.filter(user=OuterRef('user'), character__character_name__icontains=name)
        ownerships = ownerships.filter(
            Q(character__character_name__icontains=name) |
            (Exists(alts_name) & Q(character=F('user__profile__main_character')))
        )

    exclude_ids = request.GET.getlist('excludeIds', [])

    if len(exclude_ids) > 0:
        ownerships = ownerships.exclude(character_id__in=exclude_ids)

    if getattr(settings, 'PVE_ONLY_MAINS', False):
        ownerships = ownerships.filter(character=F('user__profile__main_character'))

    return JsonResponse({
        'result': [
            {
                'character_id': ownership.character_id,
                'character_name': ownership.character.character_name,
                'profile_pic': ownership.character.portrait_url_32,
                'user_id': ownership.user_id,
                'user_main_character_name': ownership.user.profile.main_character.character_name,
                'user_pic': ownership.user.profile.main_character.portrait_url_32,
                'char_status': 'Main' if ownership.character == ownership.user.profile.main_character else 'Alt',
                'char_tooltip': ownership.user.profile.main_character.character_name if ownership.character != ownership.user.profile.main_character else ', '.join(ownership.user.character_ownerships.exclude(character=ownership.character).values_list('character__character_name', flat=True))
            } for ownership in ownerships.select_related('character', 'user__profile__main_character').prefetch_related('user__character_ownerships__character').distinct()
        ],
    })


@login_required
@permission_required('allianceauth_pve.manage_entries')
def add_entry(request, rotation_id, entry_id=None):
    rotation = get_object_or_404(Rotation, pk=rotation_id)

    if rotation.is_closed:
        messages.error(request, 'The rotation is closed, you cannot add an entry')
        return redirect('allianceauth_pve:rotation_view', rotation_id)

    if entry_id:
        entry = get_object_or_404(Entry, pk=entry_id)
        if entry.rotation_id != rotation_id:
            messages.error(request, "The selected entry doesn't belong to the selected rotation")
            return redirect('allianceauth_pve:rotation_view', rotation_id)
        if entry.created_by != request.user and not request.user.is_superuser:
            messages.error(request, "You cannot edit this entry")
            return redirect('allianceauth_pve:rotation_view', rotation_id)

    if request.method == 'POST':
        copied_data = request.POST.copy()

        copied_data['estimated_total'] = copied_data['estimated_total'].replace(',', '')
        entry_form = NewEntryForm(copied_data)
        share_form = NewShareFormSet(request.POST)
        role_form = NewRoleFormSet(request.POST, prefix='roles')

        errors = check_forms_valid(role_form, entry_form, share_form)
        if len(errors) == 0:
            with transaction.atomic():
                if entry_id:
                    entry.ratting_shares.all().delete()
                    entry.roles.all().delete()
                    entry.estimated_total = entry_form.cleaned_data['estimated_total']
                    entry.save()
                else:
                    entry = Entry.objects.create(
                        rotation=rotation,
                        estimated_total=entry_form.cleaned_data['estimated_total'],
                        created_by=request.user,
                    )

                to_add = []

                for new_role in role_form.cleaned_data:
                    to_add.append(EntryRole(entry=entry, name=new_role['name'], value=new_role['value']))

                EntryRole.objects.bulk_create(to_add)
                to_add.clear()

                setups = set()

                for new_share in share_form.cleaned_data:
                    role = entry.roles.get(name=new_share['role'])

                    setup = new_share['helped_setup'] and new_share['user'] not in setups
                    if setup:
                        setups.add(new_share['user'])

                    to_add.append(EntryCharacter(
                        entry=entry,
                        role=role,
                        user_character_id=new_share['character'],
                        user_id=new_share['user'],
                        site_count=new_share['site_count'],
                        helped_setup=setup,
                    ))

                EntryCharacter.objects.bulk_create(to_add)

            messages.success(request, 'Entry added successfully')

            return redirect('allianceauth_pve:rotation_view', rotation_id)

        else:
            for error in errors:
                messages.error(request, f'Error: {error}')

    else:
        if entry_id:
            entry_form = NewEntryForm(initial={'estimated_total': entry.estimated_total})
            share_form = NewShareFormSet(initial=[
                {
                    'user': share.user_id,
                    'character': share.user_character_id,
                    'helped_setup': share.helped_setup,
                    'site_count': share.site_count,
                    'role': share.role.name,
                } for share in entry.ratting_shares.select_related('role')
            ])
            roles_choices = [(val, val) for val in entry.roles.values_list('name', flat=True)]
            for form in share_form:
                form.fields['role'].choices = roles_choices

            role_form = NewRoleFormSet(initial=[
                {
                    'name': role.name,
                    'value': role.value,
                } for role in entry.roles.all()
            ], prefix='roles')
        else:
            entry_form = NewEntryForm()
            share_form = NewShareFormSet()
            role_form = NewRoleFormSet(prefix='roles', initial=[{
                'name': 'Krab',
                'value': 1,
            }])

    context = {
        'entryform': entry_form,
        'shareforms': share_form,
        'roleforms': role_form,
        'rotation': rotation,
        'rolessetups': rotation.roles_setups.alias(roles_num=Count('roles')).filter(roles_num__gt=0),
    }

    return render(request, 'allianceauth_pve/entry_form.html', context=context)


@login_required
@permission_required('allianceauth_pve.manage_entries')
def delete_entry(request, entry_id):
    entry = get_object_or_404(Entry, pk=entry_id)
    if (entry.created_by != request.user and not request.user.is_superuser) or entry.rotation.is_closed:
        messages.error(request, "You cannot delete this entry")
        return redirect('allianceauth_pve:rotation_view', entry.rotation_id)

    rotation_id = entry.rotation_id

    entry.delete()
    messages.success(request, "Entry deleted successfully")

    return redirect('allianceauth_pve:rotation_view', rotation_id)


@login_required
@permission_required('allianceauth_pve.manage_rotations')
def create_rotation(request):
    if request.method == 'POST':
        rotation_form = NewRotationForm(request.POST)

        if rotation_form.is_valid():
            rotation = rotation_form.save()

            messages.success(request, "Rotation created successfully")
            return redirect('allianceauth_pve:rotation_view', rotation.pk)
    else:
        rotation_form = NewRotationForm()

    context = {
        'form': rotation_form,
    }

    return render(request, 'allianceauth_pve/rotation_create.html', context=context)


class EntryDetailView(DetailView):
    model = Entry
