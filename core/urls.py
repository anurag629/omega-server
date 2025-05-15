from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import os

# Make sure media directories exist
os.makedirs(os.path.join(settings.MEDIA_ROOT), exist_ok=True)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('omega_auth.urls')),  # Authentication endpoints
    path('api/agents/', include('agents.urls')),  # Agents API endpoints
    path('', include('omega.urls')),  # Include our app's URLs
    
    # Always serve media files, regardless of DEBUG setting
    # Our custom view in omega/views.py will handle this
]

# Add debug toolbar in development only
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Add Django Debug Toolbar if installed
    try:
        import debug_toolbar
        urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]
    except ImportError:
        pass 

# Add static files serving
urlpatterns += [
    path('static/<path:path>', serve, {'document_root': settings.STATIC_ROOT}),
] 