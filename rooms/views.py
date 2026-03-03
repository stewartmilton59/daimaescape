from django.shortcuts import render


def one_bedroom_villa(request):
    return render(request, 'rooms/room_detail.html')

def two_bedroom_villa(request):
    return render(request, 'rooms/two_bedroom_villa.html')

def room_list(request):
    return render(request, 'rooms/room_list.html')
