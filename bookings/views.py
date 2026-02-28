from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import date, timedelta
from django.db.models import Q
from decimal import Decimal
from .models import Booking, BookingPayment, BookingHistory
from .forms import BookingForm, QuickBookingForm, BookingSearchForm
from rooms.models import Room


def booking(request):
    """Main booking page"""
    # Check if room is preselected from URL
    selected_room = None
    room_slug = request.GET.get('room')
    if room_slug:
        try:
            selected_room = Room.objects.get(slug=room_slug, is_available=True)
        except Room.DoesNotExist:
            pass

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)

            # Set price from room - use price_per_night_tzs field
            room = booking.room
            booking.price_per_night = room.price_per_night_tzs  # Use the field directly

            # Calculate nights
            nights = (booking.check_out_date - booking.check_in_date).days

            # Calculate subtotal manually
            booking.subtotal = booking.price_per_night * Decimal(nights)

            # Calculate tax using Decimal
            TAX_RATE = Decimal('0.18')  # 18% as Decimal
            booking.tax_amount = booking.subtotal * TAX_RATE

            # Calculate total amount
            booking.total_amount = booking.subtotal + \
                booking.tax_amount - booking.discount_amount

            # Set total_nights
            booking.total_nights = nights

            booking.save()

            # Send confirmation email
            try:
                send_booking_confirmation(booking)
            except:
                # Log error but don't break the booking process
                pass

            messages.success(request, f'Booking successful! Your reference number is: {
                             booking.booking_reference}')
            return redirect('booking:booking_success', reference=booking.booking_reference)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        initial = {}
        if selected_room:
            initial['room'] = selected_room
        if request.GET.get('check_in'):
            initial['check_in_date'] = request.GET.get('check_in')
        if request.GET.get('check_out'):
            initial['check_out_date'] = request.GET.get('check_out')
        if request.GET.get('adults'):
            initial['adults'] = request.GET.get('adults')
        if request.GET.get('children'):
            initial['children'] = request.GET.get('children')

        form = BookingForm(initial=initial)

    # Get available rooms for quick display
    available_rooms = Room.objects.filter(is_available=True)[:4]

    context = {
        'form': form,
        'available_rooms': available_rooms,
        'selected_room': selected_room,
    }
    return render(request, 'bookings/booking_form.html', context)


def booking_success(request, reference):
    """Booking success page"""
    booking = get_object_or_404(Booking, booking_reference=reference)

    context = {
        'booking': booking,
    }
    return render(request, 'bookings/booking_success.html', context)


def booking_detail(request, reference):
    """View booking details"""
    booking = get_object_or_404(Booking, booking_reference=reference)

    context = {
        'booking': booking,
    }
    return render(request, 'bookings/booking_detail.html', context)


def booking_search(request):
    """Search for a booking"""
    if request.method == 'POST':
        form = BookingSearchForm(request.POST)
        if form.is_valid():
            reference = form.cleaned_data['booking_reference']
            email = form.cleaned_data['guest_email']

            try:
                booking = Booking.objects.get(
                    booking_reference=reference,
                    guest_email=email
                )
                return redirect('booking:booking_detail', reference=booking.booking_reference)
            except Booking.DoesNotExist:
                messages.error(request, 'No booking found with these details.')
    else:
        form = BookingSearchForm()

    context = {
        'form': form,
    }
    return render(request, 'bookings/booking_search.html', context)


def booking_cancel(request, reference):
    """Cancel a booking"""
    booking = get_object_or_404(Booking, booking_reference=reference)

    if not booking.can_cancel():
        messages.error(request, 'This booking cannot be cancelled.')
        return redirect('booking:booking_detail', reference=reference)

    if request.method == 'POST':
        # Update booking status
        old_status = booking.status
        booking.status = 'cancelled'
        booking.save()

        # Record in history
        BookingHistory.objects.create(
            booking=booking,
            status_from=old_status,
            status_to='cancelled',
            changed_by=request.POST.get('cancelled_by', 'Guest'),
            notes=request.POST.get('cancellation_reason', '')
        )

        # Send cancellation email
        try:
            send_cancellation_email(booking)
        except:
            pass

        messages.success(
            request, 'Your booking has been cancelled successfully.')
        return redirect('booking:booking_detail', reference=reference)

    context = {
        'booking': booking,
    }
    return render(request, 'bookings/booking_cancel.html', context)


def check_availability(request):
    """AJAX endpoint to check room availability"""
    if request.method == 'GET':
        check_in = request.GET.get('check_in')
        check_out = request.GET.get('check_out')
        adults = request.GET.get('adults', 1)

        if check_in and check_out:
            # Convert string dates to date objects
            from datetime import datetime
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()

            available_rooms = Room.objects.filter(
                is_available=True,
                max_guests__gte=adults
            ).exclude(
                Q(bookings__status__in=['confirmed', 'checked_in']) &
                Q(bookings__check_in_date__lt=check_out_date) &
                Q(bookings__check_out_date__gt=check_in_date)
            ).distinct()

            # Return JSON response for AJAX
            from django.http import JsonResponse
            rooms_data = [{
                'id': room.id,
                'name': room.name,
                'slug': room.slug,
                # Use price_per_night_tzs
                'price': float(room.price_per_night_tzs),
                'image': room.main_image.url if room.main_image and room.main_image.name else None,
                'max_guests': room.max_guests,
            } for room in available_rooms]

            return JsonResponse({'rooms': rooms_data})

    return JsonResponse({'error': 'Invalid request'}, status=400)


# Email helper functions
def send_booking_confirmation(booking):
    """Send booking confirmation email"""
    subject = f'Booking Confirmation - {booking.booking_reference}'
    message = f"""
    Dear {booking.guest_name},

    Thank you for booking with Daima Escape!

    Your booking reference: {booking.booking_reference}

    Booking Details:
    Villa: {booking.room.name}
    Check-in: {booking.check_in_date}
    Check-out: {booking.check_out_date}
    Guests: {booking.adults} Adults, {booking.children} Children
    Total Nights: {booking.total_nights}

    Price Breakdown:
    Subtotal: TSh {booking.subtotal}
    Tax (18%): TSh {booking.tax_amount}
    Total Amount: TSh {booking.total_amount}

    You can view or manage your booking at:
    http://127.0.0.1:4321/booking/detail/{booking.booking_reference}/

    We look forward to welcoming you!

    Best regards,
    Daima Escape Team
    """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL if hasattr(
            settings, 'DEFAULT_FROM_EMAIL') else 'noreply@daimaescape.com',
        [booking.guest_email],
        fail_silently=True,
    )


def send_cancellation_email(booking):
    """Send cancellation confirmation email"""
    subject = f'Booking Cancellation - {booking.booking_reference}'
    message = f"""
    Dear {booking.guest_name},

    Your booking with Daima Escape has been cancelled.

    Booking Reference: {booking.booking_reference}

    If you have made any payment, our team will contact you regarding the refund process within 3-5 business days.

    We hope to welcome you another time!

    Best regards,
    Daima Escape Team
    """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL if hasattr(
            settings, 'DEFAULT_FROM_EMAIL') else 'noreply@daimaescape.com',
        [booking.guest_email],
        fail_silently=True,
    )
