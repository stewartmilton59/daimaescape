from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('', views.booking, name='booking'),
    path('success/<str:reference>/', views.booking_success, name='booking_success'),
    path('detail/<str:reference>/', views.booking_detail, name='booking_detail'),
    path('search/', views.booking_search, name='booking_search'),
    path('cancel/<str:reference>/', views.booking_cancel, name='booking_cancel'),
    path('check-availability/', views.check_availability, name='check_availability'),
]
