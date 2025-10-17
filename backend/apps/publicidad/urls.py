from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PublicidadViewSet

# Router para los ViewSets
router = DefaultRouter()
router.register(r'publicidades', PublicidadViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
