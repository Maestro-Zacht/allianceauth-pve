from django.shortcuts import render, redirect
from django.contrib.auth.models import User

from .models import Rotation


def index(request):
    return redirect('allianceauth_pve:dashboard')


def dashboard(request):
    context = {
        'open_rots': Rotation.objects.filter(is_closed=False).order_by('-priority'),
        'closed_rots': Rotation.objects.filter(is_closed=True).order_by('-closed_at')[:10],
    }
    return render(request, 'allianceauth_pve/ratting-dashboard.html', context=context)


def rotation_view(request, rotation_id):
    r = Rotation.objects.get(pk=rotation_id)
    summary = r.summary.order_by('-estimated_total')
    summary_count_half = summary.count() // 2 + 1
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
        'entries': r.entries.order_by('-created_at')[:10],
    }

    return render(request, 'allianceauth_pve/rotation.html', context=context)
