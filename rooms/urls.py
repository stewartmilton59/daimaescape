from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    path('two-bedroom-villa/', views.two_bedroom_villa, name='two-bedroom-villa'),
    path('one-bedroom-villa/', views.one_bedroom_villa, name='one-bedroom-villa'),
    path('room-list/', views.room_detail, name='room_list'),
]
