from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.views.generic.detail import DetailView

from allianceauth.services.hooks import get_extension_logger


from .models import Entry, Rotation
from .forms import NewEntryForm, NewShareFormSet

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

    context = {
        'open_count': open_rots.count(),
        'open_rots': paginator_open.get_page(npage_open),
        'closed_rots': paginator_closed.get_page(npage_closed),
        'is_closed_param': npage_closed is not None,
    }
    return render(request, 'allianceauth_pve/ratting-dashboard.html', context=context)


@login_required
@permission_required('allianceauth_pve.access_pve')
def rotation_view(request, rotation_id):
    r = Rotation.objects.get(pk=rotation_id)
    summary = r.summary.order_by('-estimated_total').values('user', 'helped_setups', 'estimated_total', 'actual_total', character_name=F('user__profile__main_character__character_name'), character_id=F('user__profile__main_character__character_id'))
    summary_count_half = summary.count() // 2 + 1

    entries_paginator = Paginator(r.entries.order_by('-created_at'), 10)
    page = request.GET.get('page')

    context = {
        'rotation': r,
        'summary_first': summary[:summary_count_half],
        'summary_second': summary[summary_count_half:],
        'entries': entries_paginator.get_page(page),
    }

    return render(request, 'allianceauth_pve/rotation.html', context=context)


@login_required
@permission_required('allianceauth_pve.manage_entries')
def add_entry(request, rotation_id):
    rotation = Rotation.objects.get(pk=rotation_id)
    if request.method == 'POST':
        entry_form = NewEntryForm(request.POST)
        share_form = NewShareFormSet(request.POST)

        if entry_form.is_valid() and share_form.is_valid():
            # entry = entry_form.save(commit=False)

            messages.success(request, 'Entry added successfully')

            return redirect('allianceauth_pve:rotation_view', rotation_id)
        else:
            logger.debug(f'forms not valid\nentry: {entry_form.errors}\nshares:{share_form.errors}')
    else:
        entry_form = NewEntryForm()
        share_form = NewShareFormSet()

    context = {
        'entryform': entry_form,
        'shareforms': share_form,
        'rotation': rotation,
        'availableusers': User.objects.filter(
            Q(groups__permissions__codename='access_pve') |
            Q(user_permissions__codename='access_pve') |
            Q(profile__state__permissions__codename='access_pve'),
            profile__main_character__isnull=False,
        ).distinct(),
    }

    return render(request, 'allianceauth_pve/new_entry.html', context=context)


class EntryDetailView(DetailView):
    model = Entry
