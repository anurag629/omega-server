from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for DRF viewsets
router = DefaultRouter()
router.register(r'scripts', views.ManimScriptViewSet, basename='manimscript')

urlpatterns = [
    # Base views
    path('', views.HomeView.as_view(), name='home'),
    
    # API routes
    path('api/', include(router.urls)),
    path('api/generate-manim/', views.GenerateManimScriptAPIView.as_view(), name='generate-manim'),
    
    # Media serving - ensure this handles all path segments
    path('media/<path:path>', views.serve_media, name='serve-media'),
] 