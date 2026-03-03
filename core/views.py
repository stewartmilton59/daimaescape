from django.shortcuts import render


def home(request):
    return render(request, 'core/home.html')


def about(request):
    return render(request, 'core/about.html')


def contact(request):
    return render(request, 'core/contact.html')


def service(request):
    return render(request, 'core/service.html')


def house_rules(request):
    return render(request, 'core/house_rules.html', {'rules': rules})


def menu(request):
    return render(request, 'core/menu.html')


def attractions(request):
    return render(request, 'core/attractions.html')
