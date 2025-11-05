from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.views import (
    EspacioPublicitarioViewSet,
    SolicitudPublicidadViewSet,
    ItemSolicitudViewSet
)

# Router para los ViewSets
router = DefaultRouter()
router.register(r'espacios', EspacioPublicitarioViewSet, basename='publicidad_web_espacio')
router.register(r'solicitudes', SolicitudPublicidadViewSet, basename='publicidad_web_solicitud')
router.register(r'items', ItemSolicitudViewSet, basename='publicidad_web_item')

urlpatterns = [
    path('', include(router.urls)),
    
    # Endpoint para cargar archivos de publicidad (imágenes, banners, etc.)
    path(
        'items/<int:pk>/cargar-archivo/', 
        ItemSolicitudViewSet.as_view({'post': 'subir_creatividad'}), 
        name='publicidad_web_cargar_archivo'
    ),
]
