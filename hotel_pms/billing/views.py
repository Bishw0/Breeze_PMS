from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from .models import Invoice, Payment
from .forms import PaymentForm, InvoiceNotesForm


@login_required
def invoice_list(request):
    invoices = Invoice.objects.select_related(
        'reservation__guest', 'reservation__room'
    ).order_by('-created_at')

    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    if search:
        invoices = invoices.filter(
            Q(invoice_number__icontains=search) |
            Q(reservation__guest__first_name__icontains=search) |
            Q(reservation__guest__last_name__icontains=search)
        )

    total_revenue = Payment.objects.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0

    return render(request, 'billing/invoice_list.html', {
        'invoices': invoices,
        'status_choices': Invoice.STATUS_CHOICES,
        'current_status': status_filter,
        'search': search,
        'total_revenue': total_revenue,
    })


@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(
        Invoice.objects.select_related('reservation__guest', 'reservation__room'),
        pk=pk
    )
    payments = invoice.payments.order_by('-paid_at')
    service_charges = invoice.reservation.service_charges.filter(status='billed').select_related('item')
    payment_form = PaymentForm()

    return render(request, 'billing/invoice_detail.html', {
        'invoice': invoice,
        'payments': payments,
        'service_charges': service_charges,
        'payment_form': payment_form,
    })


@login_required
def add_payment(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.invoice = invoice
            payment.processed_by = request.user
            payment.save()

            # Update invoice status
            if invoice.balance_due <= 0:
                invoice.status = 'paid'
            else:
                invoice.status = 'partially_paid'
            invoice.save()
            messages.success(request, f'Payment of ${payment.amount} recorded.')
    return redirect('invoice_detail', pk=pk)


@login_required
def revenue_report(request):
    from datetime import date, timedelta
    today = date.today()
    month_start = today.replace(day=1)

    monthly_revenue = Payment.objects.filter(
        status='completed',
        paid_at__date__gte=month_start
    ).aggregate(total=Sum('amount'))['total'] or 0

    daily_revenue = Payment.objects.filter(
        status='completed',
        paid_at__date=today
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Last 30 days breakdown
    last_30 = []
    for i in range(29, -1, -1):
        day = today - timedelta(days=i)
        amount = Payment.objects.filter(
            status='completed', paid_at__date=day
        ).aggregate(total=Sum('amount'))['total'] or 0
        last_30.append({'date': day.strftime('%b %d'), 'amount': float(amount)})

    # Revenue by payment method
    by_method = Payment.objects.filter(status='completed').values('method').annotate(
        total=Sum('amount'), count=Count('id')
    ).order_by('-total')

    return render(request, 'billing/revenue_report.html', {
        'monthly_revenue': monthly_revenue,
        'daily_revenue': daily_revenue,
        'last_30_days': last_30,
        'by_method': by_method,
        'today': today,
        'month_start': month_start,
    })
