from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('team/', views.team, name='team'),
    path('service/', views.service, name='service'),
    path('testimonial/', views.testimonial, name='testimonial'),
    path('house-rules/', views.house_rules, name='house_rules'),
    path('menu/', views.menu, name='menu'),
    path('attractions/', views.attractions, name='attractions'),
]
