from django import forms
from .models import Reservation, ServiceCharge, RoomServiceItem


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = [
            'guest', 'room', 'check_in', 'check_out',
            'adults', 'children', 'rate_per_night',
            'discount_percent', 'source', 'special_requests', 'internal_notes',
        ]
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date'}),
            'check_out': forms.DateInput(attrs={'type': 'date'}),
            'special_requests': forms.Textarea(attrs={'rows': 3}),
            'internal_notes': forms.Textarea(attrs={'rows': 2}),
        }

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        room = cleaned_data.get('room')

        if check_in and check_out:
            if check_out <= check_in:
                raise forms.ValidationError('Check-out must be after check-in.')

        if room and check_in and check_out:
            instance_pk = self.instance.pk if self.instance.pk else None
            from reservations.models import Reservation
            conflicts = Reservation.objects.filter(
                room=room,
                status__in=['confirmed', 'checked_in'],
            ).exclude(check_out__lte=check_in).exclude(check_in__gte=check_out)
            if instance_pk:
                conflicts = conflicts.exclude(pk=instance_pk)
            if conflicts.exists():
                raise forms.ValidationError(
                    f'Room {room.number} is already booked for the selected dates.'
                )
        return cleaned_data


class ServiceChargeForm(forms.ModelForm):
    class Meta:
        model = ServiceCharge
        fields = ['item', 'quantity', 'unit_price', 'notes']
        widgets = {
            'notes': forms.TextInput(attrs={'placeholder': 'Optional note'}),
        }
