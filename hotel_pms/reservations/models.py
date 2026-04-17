from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]

    SOURCE_CHOICES = [
        ('direct', 'Direct / Walk-in'),
        ('phone', 'Phone'),
        ('email', 'Email'),
        ('website', 'Website'),
        ('ota', 'OTA (Booking.com, Expedia)'),
        ('travel_agent', 'Travel Agent'),
        ('corporate', 'Corporate'),
    ]

    # Core
    reservation_number = models.CharField(max_length=20, unique=True, blank=True)
    guest = models.ForeignKey('guests.Guest', on_delete=models.PROTECT, related_name='reservations')
    room = models.ForeignKey('rooms.Room', on_delete=models.PROTECT, related_name='reservations')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')

    # Dates
    check_in = models.DateField()
    check_out = models.DateField()
    actual_check_in = models.DateTimeField(null=True, blank=True)
    actual_check_out = models.DateTimeField(null=True, blank=True)

    # Guests
    adults = models.PositiveIntegerField(default=1)
    children = models.PositiveIntegerField(default=0)

    # Pricing
    rate_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='direct')

    # Additional info
    special_requests = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True, related_name='created_reservations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.reservation_number} - {self.guest} ({self.check_in} to {self.check_out})"

    def clean(self):
        if self.check_in and self.check_out:
            if self.check_out <= self.check_in:
                raise ValidationError("Check-out date must be after check-in date.")

    def save(self, *args, **kwargs):
        if not self.reservation_number:
            import random, string
            self.reservation_number = 'RES' + ''.join(
                random.choices(string.digits, k=7)
            )
        super().save(*args, **kwargs)

    @property
    def nights(self):
        if self.check_in and self.check_out:
            return (self.check_out - self.check_in).days
        return 0

    @property
    def subtotal(self):
        return self.rate_per_night * self.nights

    @property
    def discount_amount(self):
        return self.subtotal * (self.discount_percent / Decimal('100'))

    @property
    def total_room_charge(self):
        return self.subtotal - self.discount_amount


class RoomServiceItem(models.Model):
    CATEGORY_CHOICES = [
        ('food', 'Food & Beverage'),
        ('laundry', 'Laundry'),
        ('spa', 'Spa & Wellness'),
        ('transport', 'Transportation'),
        ('other', 'Other'),
    ]
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} (${self.price})"


class ServiceCharge(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('billed', 'Billed'),
        ('cancelled', 'Cancelled'),
    ]
    reservation = models.ForeignKey(
        Reservation, on_delete=models.CASCADE, related_name='service_charges'
    )
    item = models.ForeignKey(RoomServiceItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    charged_at = models.DateTimeField(auto_now_add=True)
    charged_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.item.name} x{self.quantity} for {self.reservation.reservation_number}"

    @property
    def total(self):
        return self.unit_price * self.quantity


class PricingRule(models.Model):
    RULE_TYPE_CHOICES = [
        ('percentage_adjustment', 'Percentage Adjustment'),
        ('fixed_amount_adjustment', 'Fixed Amount Adjustment'),
        ('override_rate', 'Override Rate'),
    ]

    rule_name = models.CharField(max_length=200)
    room_type = models.CharField(max_length=100, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    days_of_week = models.JSONField(blank=True, null=True)
    rule_type = models.CharField(max_length=30, choices=RULE_TYPE_CHOICES, default='percentage_adjustment')
    adjustment_value = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='NPR')
    min_stay_nights = models.IntegerField(null=True, blank=True)
    priority = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['priority']

    def __str__(self):
        return f"{self.rule_name} ({self.get_rule_type_display()})"
