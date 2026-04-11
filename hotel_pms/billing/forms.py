from django import forms
from .models import Payment, Invoice


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'method', 'transaction_ref', 'notes']
        widgets = {
            'notes': forms.TextInput(attrs={'placeholder': 'Optional reference'}),
        }


class InvoiceNotesForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['notes', 'tax_rate']
