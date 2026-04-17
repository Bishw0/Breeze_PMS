from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from decimal import Decimal
from .models import PricingRule, Reservation, ServiceCharge, RoomServiceItem
from .forms import PricingRuleForm, ReservationForm, ServiceChargeForm
from rooms.models import Room, RoomType
from billing.models import Invoice


@login_required
def dashboard(request):
    today = timezone.localdate()
    checked_in_today = Reservation.objects.filter(actual_check_in__date=today).count()
    checked_out_today = Reservation.objects.filter(actual_check_out__date=today).count()
    arrivals_today = Reservation.objects.filter(check_in=today, status='confirmed').count()
    departures_today = Reservation.objects.filter(check_out=today, status='checked_in').count()
    current_guests = Reservation.objects.filter(status='checked_in').count()
    total_rooms = Room.objects.count()
    occupied_rooms = Room.objects.filter(status='occupied').count()
    available_rooms = Room.objects.filter(status='available').count()
    occupancy_rate = round((occupied_rooms / total_rooms * 100) if total_rooms else 0, 1)

    pricing_rules = PricingRule.objects.filter(is_active=True).order_by("priority", "-created_at")
    highest_priority_rule = pricing_rules.first()

    base_room_type = RoomType.objects.order_by("id").first()
    recommended_rate = base_room_type.base_price if base_room_type else Decimal("0.00")
    if highest_priority_rule:
        if highest_priority_rule.rule_type == "percentage_adjustment":
            recommended_rate += recommended_rate * (highest_priority_rule.adjustment_value / Decimal("100"))
        elif highest_priority_rule.rule_type == "fixed_amount_adjustment":
            recommended_rate += highest_priority_rule.adjustment_value
        elif highest_priority_rule.rule_type == "override_rate":
            recommended_rate = highest_priority_rule.adjustment_value

    if occupancy_rate >= 70:
        recommended_rate += recommended_rate * Decimal("0.08")
    elif occupancy_rate >= 50:
        recommended_rate += recommended_rate * Decimal("0.04")

    recommended_rate = recommended_rate.quantize(Decimal("0.01"))

    recent_reservations = Reservation.objects.select_related(
        'guest', 'room', 'room__room_type'
    ).order_by('-created_at')[:8]

    pending_maintenance = __import__('rooms').models.MaintenanceRequest.objects.filter(
        status__in=['open', 'in_progress']
    ).count()

    context = {
        'checked_in_today': checked_in_today,
        'checked_out_today': checked_out_today,
        'arrivals_today': arrivals_today,
        'departures_today': departures_today,
        'current_guests': current_guests,
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'available_rooms': available_rooms,
        'occupancy_rate': occupancy_rate,
        'pricing_rules': pricing_rules,
        'applied_pricing_rule': highest_priority_rule,
        'recommended_rate': recommended_rate,
        'recent_reservations': recent_reservations,
        'pending_maintenance': pending_maintenance,
        'today': today,
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def reservation_list(request):
    reservations = Reservation.objects.select_related('guest', 'room', 'room__room_type').all()
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if status_filter:
        reservations = reservations.filter(status=status_filter)
    if search:
        reservations = reservations.filter(
            Q(reservation_number__icontains=search) |
            Q(guest__first_name__icontains=search) |
            Q(guest__last_name__icontains=search) |
            Q(room__number__icontains=search)
        )
    if date_from:
        reservations = reservations.filter(check_in__gte=date_from)
    if date_to:
        reservations = reservations.filter(check_out__lte=date_to)

    return render(request, 'reservations/reservation_list.html', {
        'reservations': reservations.order_by('-created_at'),
        'status_choices': Reservation.STATUS_CHOICES,
        'current_status': status_filter,
        'search': search,
        'date_from': date_from,
        'date_to': date_to,
    })


@login_required
def reservation_detail(request, pk):
    reservation = get_object_or_404(
        Reservation.objects.select_related('guest', 'room', 'room__room_type', 'created_by'),
        pk=pk
    )
    service_charges = reservation.service_charges.select_related('item').order_by('-charged_at')
    try:
        invoice = reservation.invoice
    except Invoice.DoesNotExist:
        invoice = None

    service_form = ServiceChargeForm()
    return render(request, 'reservations/reservation_detail.html', {
        'reservation': reservation,
        'service_charges': service_charges,
        'invoice': invoice,
        'service_form': service_form,
        'service_items': RoomServiceItem.objects.filter(is_active=True),
    })


@login_required
def reservation_create(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            res = form.save(commit=False)
            res.created_by = request.user
            # Set rate from room type if not overridden
            if not res.rate_per_night:
                res.rate_per_night = res.room.current_price
            res.save()
            # Update room status
            res.room.status = 'reserved'
            res.room.save()
            messages.success(request, f'Reservation {res.reservation_number} created.')
            return redirect('reservation_detail', pk=res.pk)
    else:
        initial = {}
        room_id = request.GET.get('room')
        if room_id:
            initial['room'] = room_id
        form = ReservationForm(initial=initial)
    return render(request, 'reservations/reservation_form.html', {
        'form': form, 'title': 'New Reservation'
    })


@login_required
def reservation_edit(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reservation updated.')
            return redirect('reservation_detail', pk=pk)
    else:
        form = ReservationForm(instance=reservation)
    return render(request, 'reservations/reservation_form.html', {
        'form': form,
        'title': f'Edit Reservation #{reservation.reservation_number}',
        'reservation': reservation,
    })


@login_required
def reservation_checkin(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if reservation.status == 'confirmed':
        reservation.status = 'checked_in'
        reservation.actual_check_in = timezone.now()
        reservation.save()
        reservation.room.status = 'occupied'
        reservation.room.save()
        messages.success(request, f'Guest {reservation.guest.full_name} checked in to Room {reservation.room.number}.')
    else:
        messages.error(request, 'Cannot check in: reservation is not confirmed.')
    return redirect('reservation_detail', pk=pk)


@login_required
def reservation_checkout(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if reservation.status == 'checked_in':
        reservation.status = 'checked_out'
        reservation.actual_check_out = timezone.now()
        reservation.save()
        reservation.room.status = 'cleaning'
        reservation.room.save()
        # Auto-generate invoice if not exists
        invoice, created = Invoice.objects.get_or_create(reservation=reservation)
        if created:
            from django.utils import timezone as tz
            import datetime
            invoice.status = 'issued'
            invoice.issued_at = tz.now()
            invoice.due_date = tz.localdate() + datetime.timedelta(days=7)
            invoice.save()
        messages.success(request, f'Guest checked out. Invoice #{invoice.invoice_number} generated.')
        return redirect('invoice_detail', pk=invoice.pk)
    else:
        messages.error(request, 'Cannot check out: guest is not currently checked in.')
    return redirect('reservation_detail', pk=pk)


@login_required
def reservation_cancel(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if reservation.status in ['pending', 'confirmed']:
        reservation.status = 'cancelled'
        reservation.save()
        if reservation.room.status == 'reserved':
            reservation.room.status = 'available'
            reservation.room.save()
        messages.success(request, 'Reservation cancelled.')
    else:
        messages.error(request, 'Cannot cancel this reservation.')
    return redirect('reservation_detail', pk=pk)


@login_required
def add_service_charge(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if request.method == 'POST':
        form = ServiceChargeForm(request.POST)
        if form.is_valid():
            charge = form.save(commit=False)
            charge.reservation = reservation
            charge.charged_by = request.user
            charge.save()
            messages.success(request, 'Service charge added.')
    return redirect('reservation_detail', pk=pk)


@login_required
def pricing_rule_list(request):
    pricing_rules = PricingRule.objects.all().order_by("priority", "-created_at")
    return render(request, "reservations/pricing_list.html", {"pricing_rules": pricing_rules})


@login_required
def pricing_rule_create(request):
    if request.method == "POST":
        form = PricingRuleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Pricing rule created.")
            return redirect("pricing_rule_list")
    else:
        form = PricingRuleForm()

    return render(
        request,
        "reservations/pricing_form.html",
        {
            "form": form,
            "title": "Create Pricing Rule",
        },
    )
