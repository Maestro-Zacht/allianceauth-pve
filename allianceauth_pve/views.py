from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required

from . import __version__


@login_required
@permission_required('allianceauth_pve.access_pve')
def index(request):
    return redirect('allianceauth_pve:react_view')


@login_required
@permission_required('allianceauth_pve.access_pve')
def react_view(request):
    context = {
        'version': __version__,
    }

    return render(request, 'allianceauth_pve/react_base.html', context=context)
