from django.shortcuts import render
from rooms.models import Room, HouseRule, LaundryService


def home(request):
    # Get featured villas that are available
    featured_villas = Room.objects.filter(
        is_available=True, is_featured=True)[:3]

    # If no featured villas, get any 3 available villas
    if not featured_villas:
        featured_villas = Room.objects.filter(is_available=True)[:3]

    # Get house rules for display (optional)
    house_rules = HouseRule.objects.all()[:6]

    # Get laundry services
    laundry_services = LaundryService.objects.all()

    context = {
        # Keep same variable name for template compatibility
        'featured_rooms': featured_villas,
        'featured_villas': featured_villas,
        'house_rules': house_rules,
        'laundry_services': laundry_services,
    }

    # Get featured rooms that are available, limit to 3 for home page
    featured_rooms = Room.objects.filter(
        is_available=True, is_featured=True)[:3]

    # If no featured rooms, get any 3 available rooms
    if not featured_rooms:
        featured_rooms = Room.objects.filter(is_available=True)[:3]

    context = {
        'featured_rooms': featured_rooms,
    }
    return render(request, 'core/home.html', context)


def about(request):
    return render(request, 'core/about.html')


def contact(request):
    return render(request, 'core/contact.html')


def service(request):
    return render(request, 'core/service.html')


def team(request):
    return render(request, 'core/team.html')


def testimonial(request):
    return render(request, 'core/testimonial.html')


def house_rules(request):
    """Display all house rules"""
    from rooms.models import HouseRule
    rules = HouseRule.objects.all()
    return render(request, 'core/house_rules.html', {'rules': rules})


def menu(request):
    """Display restaurant menu"""
    return render(request, 'core/menu.html')


def attractions(request):
    """Display local attractions"""
    return render(request, 'core/attractions.html')
