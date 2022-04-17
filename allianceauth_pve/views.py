from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.db import transaction
from django.views.generic.detail import DetailView

from allianceauth.services.hooks import get_extension_logger


from .models import Entry, EntryCharacter, Rotation
from .forms import NewEntryForm, NewShareFormSet
from .utils import ratting_users

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

                for new_share in share_form.cleaned_data:
                    if len(new_share) > 0 and not new_share.get('DELETE', False):
                        to_add.append(EntryCharacter(
                            entry=entry,
                            user=User.objects.get(profile__main_character__character_name=new_share['user']),
                            share_count=new_share['share_count'],
                            helped_setup=new_share['helped_setup'],
                        ))

                EntryCharacter.objects.bulk_create(to_add)

                entry.update_share_totals()

            messages.success(request, 'Entry added successfully')

            return redirect('allianceauth_pve:rotation_view', rotation_id)
        else:
            logger.debug(f'forms not valid\nentry: {entry_form.errors}\nshares:{share_form.errors}')
    else:
        if entry_id:
            entry_form = NewEntryForm(initial={'estimated_total': entry.estimated_total})
            share_form = NewShareFormSet(initial=[
                {
                    'user': share.user.profile.main_character.character_name,
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
        'availableusers': ratting_users,
    }

    return render(request, 'allianceauth_pve/new_entry.html', context=context)


class EntryDetailView(DetailView):
    model = Entry
