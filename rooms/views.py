from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Room


def room_list(request):
    return render(request, 'rooms/room_detail.html', context)
