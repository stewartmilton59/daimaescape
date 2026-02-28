from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
from .models import Booking, BookingPayment
from rooms.models import Room


class BookingForm(forms.ModelForm):
    """Main booking form for guests"""

    class Meta:
        model = Booking
        fields = [
            'room', 'guest_name', 'guest_email', 'guest_phone', 'guest_address',
            'check_in_date', 'check_out_date', 'adults', 'children',
            'special_requests'
        ]
        widgets = {
            'check_in_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'check_out_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'guest_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
            'guest_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'guest_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
            'guest_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter your address'}),
            'adults': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'children': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 6}),
            'special_requests': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Any special requests? (optional)'}),
            'room': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show available rooms
        self.fields['room'].queryset = Room.objects.filter(is_available=True)
        self.fields['room'].empty_label = "Select a Room"

        # Set minimum dates
        today = date.today()
        self.fields['check_in_date'].widget.attrs['min'] = today.isoformat()
        self.fields['check_out_date'].widget.attrs['min'] = (
            today + timedelta(days=1)).isoformat()

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')
        room = cleaned_data.get('room')

        if check_in and check_out:
            # Check if check-out is after check-in
            if check_out <= check_in:
                raise ValidationError(
                    "Check-out date must be after check-in date.")

            # Check if dates are in the past
            if check_in < date.today():
                raise ValidationError("Check-in date cannot be in the past.")

            # Check room availability
            if room:
                overlapping_bookings = Booking.objects.filter(
                    room=room,
                    status__in=['confirmed', 'checked_in'],
                    check_in_date__lt=check_out,
                    check_out_date__gt=check_in
                )
                if overlapping_bookings.exists():
                    raise ValidationError(
                        "This room is not available for the selected dates.")

        return cleaned_data


class QuickBookingForm(forms.Form):
    """Quick booking form for homepage"""
    check_in = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'Check In'})
    )
    check_out = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'Check Out'})
    )
    adults = forms.IntegerField(
        initial=2,
        min_value=1, max_value=10,
        widget=forms.NumberInput(
            attrs={'class': 'form-control', 'placeholder': 'Adults'})
    )
    children = forms.IntegerField(
        initial=0,
        min_value=0, max_value=6,
        widget=forms.NumberInput(
            attrs={'class': 'form-control', 'placeholder': 'Children'})
    )

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')

        if check_in and check_out:
            if check_out <= check_in:
                raise ValidationError("Check-out must be after check-in")
            if check_in < date.today():
                raise ValidationError("Check-in cannot be in the past")

        return cleaned_data


class BookingSearchForm(forms.Form):
    """Form for searching bookings"""
    booking_reference = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter your booking reference'})
    )
    guest_email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )
