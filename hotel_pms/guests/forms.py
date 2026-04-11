from django import forms
from .models import Guest


class GuestForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'date_of_birth',
            'nationality', 'id_type', 'id_number',
            'address_line1', 'address_line2', 'city', 'country', 'postal_code',
            'preferences', 'vip_status',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'preferences': forms.Textarea(attrs={'rows': 3}),
        }
