from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for the API
router = DefaultRouter()
router.register(r'scripts', views.ScriptViewSet)
router.register(r'executions', views.ExecutionViewSet)
router.register(r'providers', views.AIProviderViewSet)
router.register(r'containers', views.ContainerViewSet)

urlpatterns = [
    # Include the router URLs
    path('', include(router.urls)),
] 