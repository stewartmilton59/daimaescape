from django.shortcuts import render

def booking(request):
    return render(request, 'bookings/booking_form.html')

def booking_success(request):
    return render(request, 'bookings/booking_success.html')

def booking_detail(request, reference):
    return render(request, 'bookings/booking_search.html')

def booking_cancel(request, reference):
    return render(request, 'bookings/booking_cancel.html')

def check_availability(request):
    return render(request, 'bookings/check_availability.html')

def booking_search(request):
    return render(request, 'bookings/booking_search.html')