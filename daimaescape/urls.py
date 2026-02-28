from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path

urlpatterns = [
    path('staff/', admin.site.urls),
    path('', include('core.urls')),
    path('rooms/', include('rooms.urls')),
    path('booking/', include('bookings.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
else:
    # For production with DEBUG=False, we still need to serve media files
    # In production, you should configure your web server to serve these
    # But for local testing, this helps
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve,
                {'document_root': settings.MEDIA_ROOT}),
        re_path(r'^static/(?P<path>.*)$', serve,
                {'document_root': settings.STATIC_ROOT}),
    ]
