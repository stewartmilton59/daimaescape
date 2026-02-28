from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Room


def room_list(request):
    """Display all available rooms with filtering"""
    rooms = Room.objects.filter(is_available=True)

    # Filtering
    room_type = request.GET.get('type')
    if room_type:
        rooms = rooms.filter(room_type=room_type)

    # Search
    search_query = request.GET.get('search')
    if search_query:
        rooms = rooms.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(short_description__icontains=search_query)
        )

    # Price range filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        rooms = rooms.filter(price_per_night__gte=min_price)
    if max_price:
        rooms = rooms.filter(price_per_night__lte=max_price)

    # Featured rooms first
    rooms = rooms.order_by('-is_featured', 'name')

    # Pagination
    paginator = Paginator(rooms, 6)  # Show 6 rooms per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'rooms': page_obj,
        'room_types': Room.ROOM_TYPES,
        'current_type': room_type,
        'search_query': search_query,
    }
    return render(request, 'rooms/room_list.html', context)


def room_detail(request, slug):
    """Display single room details"""
    room = get_object_or_404(Room, slug=slug, is_available=True)

    # Get similar rooms (same type, exclude current)
    similar_rooms = Room.objects.filter(
        room_type=room.room_type,
        is_available=True
    ).exclude(id=room.id)[:3]

    context = {
        'room': room,
        'similar_rooms': similar_rooms,
    }
    return render(request, 'rooms/room_detail.html', context)
