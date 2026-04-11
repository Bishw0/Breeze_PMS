from django import forms
from .models import Room, RoomType, MaintenanceRequest


class RoomTypeForm(forms.ModelForm):
    class Meta:
        model = RoomType
        fields = ['name', 'description', 'base_price', 'capacity', 'amenities']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'amenities': forms.TextInput(attrs={'placeholder': 'WiFi, TV, Mini Bar, ...'}),
        }


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['number', 'room_type', 'floor', 'status', 'is_smoking', 'has_view', 'price_override', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class MaintenanceRequestForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ['room', 'title', 'description', 'priority', 'status', 'assigned_to']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
