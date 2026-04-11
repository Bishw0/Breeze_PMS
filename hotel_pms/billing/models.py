from django.db import models
from decimal import Decimal


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'),
        ('void', 'Void'),
    ]

    invoice_number = models.CharField(max_length=20, unique=True, blank=True)
    reservation = models.OneToOneField(
        'reservations.Reservation', on_delete=models.PROTECT, related_name='invoice'
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('13.00'))
    notes = models.TextField(blank=True)

    issued_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            import random, string
            self.invoice_number = 'INV' + ''.join(random.choices(string.digits, k=7))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice #{self.invoice_number}"

    @property
    def room_charge(self):
        return self.reservation.total_room_charge

    @property
    def service_charges_total(self):
        from reservations.models import ServiceCharge
        from django.db.models import Sum
        result = self.reservation.service_charges.filter(
            status='billed'
        ).aggregate(total=Sum('unit_price'))
        return result['total'] or Decimal('0')

    @property
    def subtotal(self):
        return self.room_charge + self.service_charges_total

    @property
    def tax_amount(self):
        return self.subtotal * (self.tax_rate / Decimal('100'))

    @property
    def total_amount(self):
        return self.subtotal + self.tax_amount

    @property
    def amount_paid(self):
        from django.db.models import Sum
        result = self.payments.filter(status='completed').aggregate(total=Sum('amount'))
        return result['total'] or Decimal('0')

    @property
    def balance_due(self):
        return self.total_amount - self.amount_paid


class Payment(models.Model):
    METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('online', 'Online Payment'),
        ('cheque', 'Cheque'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='cash')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='completed')
    transaction_ref = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    processed_by = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True
    )
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment of ${self.amount} for {self.invoice}"
