from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from apps.publicidad.models import (
    EspacioPublicitario, 
    SolicitudPublicidad, 
    ItemSolicitud, 
    CreatividadPublicitaria
)
from .serializers import (
    EspacioPublicitarioSerializer,
    SolicitudPublicidadSerializer,
    ItemSolicitudSerializer,
    CreatividadPublicitariaSerializer
)

class EspacioPublicitarioViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar los espacios publicitarios.
    """
    queryset = EspacioPublicitario.objects.all()
    serializer_class = EspacioPublicitarioSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = []  # No authentication needed for viewing
        else:
            permission_classes = [IsAuthenticated]  # Authentication needed for other actions
        return [permission() for permission in permission_classes]

class SolicitudPublicidadViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar solicitudes de publicidad.
    Los usuarios solo pueden ver sus propias solicitudes.
    Los administradores pueden ver todas las solicitudes.
    """
    serializer_class = SolicitudPublicidadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return SolicitudPublicidad.objects.all()
        return SolicitudPublicidad.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

class ItemSolicitudViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar los items de las solicitudes de publicidad.
    """
    serializer_class = ItemSolicitudSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return ItemSolicitud.objects.all()
        return ItemSolicitud.objects.filter(solicitud__usuario=self.request.user)

    @action(detail=True, methods=['post'])
    def cargar_archivo(self, request, pk=None):
        """
        Endpoint para cargar archivos de publicidad (imágenes, banners, etc.)
        para un ítem de solicitud de publicidad.
        
        Parámetros:
        - archivo: El archivo a subir (imagen, banner, etc.)
        
        Retorna:
        - 201: Archivo cargado exitosamente
        - 400: Error en la solicitud (archivo no proporcionado o inválido)
        - 404: El ítem no existe
        """
        try:
            item = self.get_object()
            if 'archivo' not in request.FILES:
                return Response(
                    {"error": "No se proporcionó ningún archivo"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            archivo = request.FILES['archivo']
            
            # Crear o actualizar la creatividad
            creatividad, created = CreatividadPublicitaria.objects.update_or_create(
                item=item,
                defaults={'archivo': archivo}
            )
            
            # Validar la creatividad
            creatividad.full_clean()
            creatividad.save()
            
            serializer = CreatividadPublicitariaSerializer(creatividad)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except ItemSolicitud.DoesNotExist:
            return Response(
                {"error": "El ítem de solicitud no existe"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
