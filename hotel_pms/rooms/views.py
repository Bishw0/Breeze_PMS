from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Room, RoomType, MaintenanceRequest
from .forms import RoomForm, RoomTypeForm, MaintenanceRequestForm


@login_required
def room_list(request):
    rooms = Room.objects.select_related('room_type').all()
    status_filter = request.GET.get('status', '')
    floor_filter = request.GET.get('floor', '')
    type_filter = request.GET.get('type', '')
    search = request.GET.get('search', '')

    if status_filter:
        rooms = rooms.filter(status=status_filter)
    if floor_filter:
        rooms = rooms.filter(floor=floor_filter)
    if type_filter:
        rooms = rooms.filter(room_type_id=type_filter)
    if search:
        rooms = rooms.filter(number__icontains=search)

    room_types = RoomType.objects.all()
    floors = range(1, 21)
    status_counts = {s[0]: Room.objects.filter(status=s[0]).count() for s in Room.STATUS_CHOICES}

    context = {
        'rooms': rooms,
        'room_types': room_types,
        'floors': floors,
        'status_choices': Room.STATUS_CHOICES,
        'status_counts': status_counts,
        'current_filters': {
            'status': status_filter,
            'floor': floor_filter,
            'type': type_filter,
            'search': search,
        }
    }
    return render(request, 'rooms/room_list.html', context)


@login_required
def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)
    upcoming = room.reservations.filter(status__in=['confirmed', 'pending']).order_by('check_in')[:5]
    maintenance = room.maintenance_requests.order_by('-created_at')[:5]
    return render(request, 'rooms/room_detail.html', {
        'room': room,
        'upcoming_reservations': upcoming,
        'maintenance_requests': maintenance,
    })


@login_required
def room_create(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save()
            messages.success(request, f'Room {room.number} created successfully.')
            return redirect('room_detail', pk=room.pk)
    else:
        form = RoomForm()
    return render(request, 'rooms/room_form.html', {'form': form, 'title': 'Add New Room'})


@login_required
def room_edit(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, f'Room {room.number} updated successfully.')
            return redirect('room_detail', pk=room.pk)
    else:
        form = RoomForm(instance=room)
    return render(request, 'rooms/room_form.html', {'form': form, 'title': f'Edit Room {room.number}', 'room': room})


@login_required
def room_status_update(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_statuses = [s[0] for s in Room.STATUS_CHOICES]
        if new_status in valid_statuses:
            room.status = new_status
            if new_status == 'available':
                from django.utils import timezone
                room.last_cleaned = timezone.now()
            room.save()
            messages.success(request, f'Room {room.number} status updated to {room.get_status_display()}.')
    return redirect('room_detail', pk=pk)


@login_required
def maintenance_list(request):
    requests = MaintenanceRequest.objects.select_related('room', 'reported_by').order_by('-created_at')
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    if status_filter:
        requests = requests.filter(status=status_filter)
    if priority_filter:
        requests = requests.filter(priority=priority_filter)
    return render(request, 'rooms/maintenance_list.html', {
        'requests': requests,
        'status_choices': MaintenanceRequest.STATUS_CHOICES,
        'priority_choices': MaintenanceRequest.PRIORITY_CHOICES,
        'current_status': status_filter,
        'current_priority': priority_filter,
    })


@login_required
def maintenance_create(request, room_pk=None):
    initial = {}
    if room_pk:
        room = get_object_or_404(Room, pk=room_pk)
        initial['room'] = room
    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST)
        if form.is_valid():
            mr = form.save(commit=False)
            mr.reported_by = request.user
            mr.save()
            room = mr.room
            room.status = 'maintenance'
            room.save()
            messages.success(request, 'Maintenance request submitted.')
            return redirect('maintenance_list')
    else:
        form = MaintenanceRequestForm(initial=initial)
    return render(request, 'rooms/maintenance_form.html', {'form': form})


@login_required
def maintenance_update(request, pk):
    mr = get_object_or_404(MaintenanceRequest, pk=pk)
    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST, instance=mr)
        if form.is_valid():
            updated = form.save()
            if updated.status == 'resolved':
                from django.utils import timezone
                updated.resolved_at = timezone.now()
                updated.save()
                updated.room.status = 'cleaning'
                updated.room.save()
            messages.success(request, 'Maintenance request updated.')
            return redirect('maintenance_list')
    else:
        form = MaintenanceRequestForm(instance=mr)
    return render(request, 'rooms/maintenance_form.html', {'form': form, 'request_obj': mr})
