from django.db import models


class Guest(models.Model):
    ID_TYPE_CHOICES = [
        ('passport', 'Passport'),
        ('national_id', 'National ID'),
        ('driving_license', "Driver's License"),
        ('other', 'Other'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    date_of_birth = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    id_type = models.CharField(max_length=20, choices=ID_TYPE_CHOICES, default='passport')
    id_number = models.CharField(max_length=50, blank=True)

    # Address
    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)

    # Preferences
    preferences = models.TextField(blank=True, help_text="Special requests or preferences")
    vip_status = models.BooleanField(default=False)
    blacklisted = models.BooleanField(default=False)
    blacklist_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def total_stays(self):
        return self.reservations.filter(status='checked_out').count()

    @property
    def total_spent(self):
        from billing.models import Invoice
        from django.db.models import Sum
        result = Invoice.objects.filter(
            reservation__guest=self, status='paid'
        ).aggregate(total=Sum('total_amount'))
        return result['total'] or 0
