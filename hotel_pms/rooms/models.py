from django.db import models


class RoomType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField(default=2)
    amenities = models.TextField(blank=True, help_text="Comma-separated list of amenities")

    def __str__(self):
        return self.name

    def amenities_list(self):
        return [a.strip() for a in self.amenities.split(',') if a.strip()]


class Room(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Under Maintenance'),
        ('cleaning', 'Being Cleaned'),
        ('reserved', 'Reserved'),
    ]

    FLOOR_CHOICES = [(i, f'Floor {i}') for i in range(1, 21)]

    number = models.CharField(max_length=10, unique=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.PROTECT, related_name='rooms')
    floor = models.PositiveIntegerField(choices=FLOOR_CHOICES, default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    notes = models.TextField(blank=True)
    is_smoking = models.BooleanField(default=False)
    has_view = models.BooleanField(default=False)
    price_override = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Override base price for this specific room"
    )
    last_cleaned = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f"Room {self.number} ({self.room_type.name})"

    @property
    def current_price(self):
        return self.price_override if self.price_override else self.room_type.base_price

    def is_available_for_dates(self, check_in, check_out):
        from reservations.models import Reservation
        conflicting = Reservation.objects.filter(
            room=self,
            status__in=['confirmed', 'checked_in'],
        ).exclude(check_out__lte=check_in).exclude(check_in__gte=check_out)
        return not conflicting.exists()


class MaintenanceRequest(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='maintenance_requests')
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')
    reported_by = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True, related_name='reported_issues'
    )
    assigned_to = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_issues'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.room} - {self.title}"
