import datetime
from django.http import JsonResponse

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.db import transaction
from django.views.generic.detail import DetailView

from allianceauth.services.hooks import get_extension_logger

from .models import Entry, EntryCharacter, Rotation
from .forms import NewEntryForm, NewShareFormSet, NewRotationForm, CloseRotationForm
from .actions import running_averages

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
    r = Rotation.objects.get(pk=rotation_id)

    if request.method == 'POST':
        closeform = CloseRotationForm(request.POST)

        if closeform.is_valid():
            with transaction.atomic():
                r.actual_total = closeform.cleaned_data['sales_value']
                r.is_closed = True
                r.closed_at = timezone.now()
                r.save()
                for entry in r.entries.all():
                    entry.update_share_totals()

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
        'summary_first': summary[:summary_count_half],
        'summary_second': summary[summary_count_half:],
        'entries': entries_paginator.get_page(page),
        'closeform': closeform,
    }

    return render(request, 'allianceauth_pve/rotation.html', context=context)


@login_required
@permission_required('allianceauth_pve.manage_entries')
def get_avaiable_ratters(request, name=None):
    ratting_users = User.objects.filter(
        Q(groups__permissions__codename='access_pve') |
        Q(user_permissions__codename='access_pve') |
        Q(profile__state__permissions__codename='access_pve'),
        profile__main_character__isnull=False,
    )

    if name:
        ratting_users = ratting_users.filter(profile__main_character__character_name__icontains=name)

    exclude_ids = request.GET.getlist('excludeIds', [])

    logger.debug(exclude_ids)

    if len(exclude_ids) > 0:
        ratting_users = ratting_users.exclude(pk__in=exclude_ids)

    ratting_users = ratting_users.distinct()

    return JsonResponse({
        'result': [
            {
                'character_name': user.profile.main_character.character_name,
                'profile_pic': user.profile.main_character.portrait_url_32,
                'user_id': user.pk,
            } for user in ratting_users
        ],
    })


@login_required
@permission_required('allianceauth_pve.manage_entries')
def add_entry(request, rotation_id, entry_id=None):
    rotation = Rotation.objects.get(pk=rotation_id)
    if entry_id:
        entry = Entry.objects.get(pk=entry_id)
        if entry.rotation != rotation:
            messages.error(request, "The selected entry doesn't belong to the selected rotation")
            return redirect('allianceauth_pve:rotation_view', rotation_id)
        if entry.created_by != request.user and not request.user.is_superuser:
            messages.error(request, "You cannot edit this entry")
            return redirect('allianceauth_pve:rotation_view', rotation_id)

    if request.method == 'POST':
        entry_form = NewEntryForm(request.POST)
        share_form = NewShareFormSet(request.POST)

        if entry_form.is_valid() and share_form.is_valid():
            with transaction.atomic():
                if entry_id:
                    entry.ratting_shares.all().delete()
                    entry.estimated_total = entry_form.cleaned_data['estimated_total']
                else:
                    entry = Entry.objects.create(
                        rotation=rotation,
                        estimated_total=entry_form.cleaned_data['estimated_total'],
                        created_by=request.user,
                    )

                to_add = []
                characters = set()

                for new_share in share_form.cleaned_data:
                    if len(new_share) > 0 and not new_share.get('DELETE', False):
                        person = User.objects.get(pk=new_share['user'])
                        if person.pk not in characters:
                            to_add.append(EntryCharacter(
                                entry=entry,
                                user=person,
                                share_count=new_share['share_count'],
                                helped_setup=new_share['helped_setup'],
                            ))
                            characters.add(person.pk)

                EntryCharacter.objects.bulk_create(to_add)

                entry.update_share_totals()

            messages.success(request, 'Entry added successfully')

            return redirect('allianceauth_pve:rotation_view', rotation_id)
        else:
            logger.error(f'forms not valid\nentry: {entry_form.errors}\nshares:{share_form.errors}')

    else:
        if entry_id:
            entry_form = NewEntryForm(initial={'estimated_total': entry.estimated_total})
            share_form = NewShareFormSet(initial=[
                {
                    'user': share.user_id,
                    'helped_setup': share.helped_setup,
                    'share_count': share.share_count,
                } for share in entry.ratting_shares.all()
            ])
        else:
            entry_form = NewEntryForm()
            share_form = NewShareFormSet()

    context = {
        'entryform': entry_form,
        'shareforms': share_form,
        'rotation': rotation,
    }

    return render(request, 'allianceauth_pve/entry_form.html', context=context)


@login_required
@permission_required('allianceauth_pve.manage_entries')
def delete_entry(request, entry_id):
    entry = get_object_or_404(Entry, pk=entry_id)
    if entry.created_by != request.user and not request.user.is_superuser:
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
