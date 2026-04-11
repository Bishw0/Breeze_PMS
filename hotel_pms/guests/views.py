from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Guest
from .forms import GuestForm


@login_required
def guest_list(request):
    guests = Guest.objects.all()
    search = request.GET.get('search', '')
    vip_only = request.GET.get('vip', '')

    if search:
        guests = guests.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )
    if vip_only:
        guests = guests.filter(vip_status=True)

    return render(request, 'guests/guest_list.html', {
        'guests': guests,
        'search': search,
        'vip_only': vip_only,
        'total_count': Guest.objects.count(),
        'vip_count': Guest.objects.filter(vip_status=True).count(),
    })


@login_required
def guest_detail(request, pk):
    guest = get_object_or_404(Guest, pk=pk)
    reservations = guest.reservations.select_related('room', 'room__room_type').order_by('-check_in')
    return render(request, 'guests/guest_detail.html', {
        'guest': guest,
        'reservations': reservations,
    })


@login_required
def guest_create(request):
    if request.method == 'POST':
        form = GuestForm(request.POST)
        if form.is_valid():
            guest = form.save()
            messages.success(request, f'Guest {guest.full_name} created successfully.')
            return redirect('guest_detail', pk=guest.pk)
    else:
        form = GuestForm()
    return render(request, 'guests/guest_form.html', {'form': form, 'title': 'Add New Guest'})


@login_required
def guest_edit(request, pk):
    guest = get_object_or_404(Guest, pk=pk)
    if request.method == 'POST':
        form = GuestForm(request.POST, instance=guest)
        if form.is_valid():
            form.save()
            messages.success(request, f'Guest {guest.full_name} updated.')
            return redirect('guest_detail', pk=guest.pk)
    else:
        form = GuestForm(instance=guest)
    return render(request, 'guests/guest_form.html', {'form': form, 'title': f'Edit {guest.full_name}', 'guest': guest})
