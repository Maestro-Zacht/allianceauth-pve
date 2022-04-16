from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.models import User

from allianceauth.services.hooks import get_extension_logger


from .models import Rotation

logger = get_extension_logger(__name__)


def index(request):
    return redirect('allianceauth_pve:dashboard')


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


def rotation_view(request, rotation_id):
    r = Rotation.objects.get(pk=rotation_id)
    summary = r.summary.order_by('-estimated_total')
    summary_count_half = summary.count() // 2 + 1

    entries_paginator = Paginator(r.entries.order_by('-created_at'), 10)
    page = request.GET.get('page')

    context = {
        'rotation': r,
        'summary_first': [
            {
                'character': User.objects.get(pk=row['user']).profile.main_character,
                **row,
            } for row in summary[:summary_count_half]
        ],
        'summary_second': [
            {
                'character': User.objects.get(pk=row['user']).profile.main_character,
                **row,
            } for row in summary[summary_count_half:]
        ],
        'entries': entries_paginator.get_page(page),
    }

    return render(request, 'allianceauth_pve/rotation.html', context=context)
