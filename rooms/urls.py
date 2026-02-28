from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    path('', views.room_list, name='room_list'),
    path('room/<slug:slug>/', views.room_detail, name='room_detail'),
]
