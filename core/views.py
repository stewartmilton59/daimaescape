from django.shortcuts import render


def home(request):
    return render(request, 'core/home.html')


def about(request):
    return render(request, 'core/about.html')


def contact(request):
    return render(request, 'core/contact.html')


def service(request):
    return render(request, 'core/service.html')


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
