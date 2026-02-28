from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, EmailValidator
from django.utils import timezone
from datetime import date, timedelta
from rooms.models import Room


class Booking(models.Model):
    BOOKING_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]

    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('bank', 'Bank Transfer'),
        ('mobile', 'Mobile Money'),
    ]

    # Booking Reference
    booking_reference = models.CharField(
        max_length=20, unique=True, editable=False)

    # Room Information
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name='bookings')

    # Guest Information
    guest_name = models.CharField(max_length=100)
    guest_email = models.EmailField(validators=[EmailValidator()])
    guest_phone = models.CharField(max_length=20)
    guest_address = models.TextField(blank=True)

    # Identification
    id_type = models.CharField(max_length=50, blank=True,
                               choices=[('passport', 'Passport'),
                                        ('id_card', 'ID Card'),
                                        ('drivers_license', "Driver's License")])
    id_number = models.CharField(max_length=50, blank=True)

    # Booking Details
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    adults = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    children = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(6)])

    price_per_night = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    total_nights = models.PositiveIntegerField(editable=False, default=0)
    subtotal = models.DecimalField(
        max_digits=10, decimal_places=2, editable=False, default=0)
    tax_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, editable=False, default=0)
    # Special Requests
    special_requests = models.TextField(blank=True)

    # Status
    status = models.CharField(
        max_length=20, choices=BOOKING_STATUS, default='pending')
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHODS, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    checked_out_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['booking_reference']),
            models.Index(fields=['check_in_date', 'check_out_date']),
            models.Index(fields=['status', 'payment_status']),
        ]

    def __str__(self):
        return f"{self.booking_reference} - {self.guest_name}"

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = self.generate_booking_reference()

        # Calculate nights and totals
        self.total_nights = (self.check_out_date - self.check_in_date).days
        self.subtotal = self.price_per_night * self.total_nights
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount

        super().save(*args, **kwargs)

    def generate_booking_reference(self):
        """Generate unique booking reference"""
        import random
        import string
        from datetime import datetime

        # Format: DMY-XXXXX (e.g., 270224-AB123)
        date_part = datetime.now().strftime('%d%m%y')
        random_part = ''.join(random.choices(
            string.ascii_uppercase + string.digits, k=5))
        reference = f"{date_part}-{random_part}"

        # Ensure uniqueness
        while Booking.objects.filter(booking_reference=reference).exists():
            random_part = ''.join(random.choices(
                string.ascii_uppercase + string.digits, k=5))
            reference = f"{date_part}-{random_part}"

        return reference

    def get_nights(self):
        return (self.check_out_date - self.check_in_date).days

    def is_active(self):
        return self.status in ['confirmed', 'checked_in']

    def can_cancel(self):
        return self.status in ['pending', 'confirmed'] and self.check_in_date > date.today()


class BookingPayment(models.Model):
    """Track multiple payments for a booking"""
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(
        max_length=20, choices=Booking.PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    paid_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-paid_at']


class BookingHistory(models.Model):
    """Track booking status changes"""
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name='history')
    status_from = models.CharField(max_length=20)
    status_to = models.CharField(max_length=20)
    changed_by = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']
        verbose_name_plural = "Booking histories"
