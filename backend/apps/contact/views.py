from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from .models import TipoAsunto, Estado, Contacto, Suscripcion
from .serializers import (
    TipoAsuntoSerializer, EstadoSerializer, ContactoSerializer, ContactoCreateSerializer,
    SuscripcionSerializer, SuscripcionCreateSerializer, ContactMessageLegacySerializer,
    SubscriptionLegacySerializer
)

# ViewSets normalizados
class TipoAsuntoViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para tipos de asunto (solo lectura)"""
    queryset = TipoAsunto.objects.all()
    serializer_class = TipoAsuntoSerializer
    permission_classes = [AllowAny]

class EstadoViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para estados (solo lectura)"""
    queryset = Estado.objects.all()
    serializer_class = EstadoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['get'])
    def por_tipo(self, request):
        """Obtener estados por tipo de entidad"""
        tipo = request.query_params.get('tipo')
        if tipo:
            estados = self.queryset.filter(tipo_entidad=tipo)
            serializer = self.get_serializer(estados, many=True)
            return Response(serializer.data)
        return Response([])

class ContactoViewSet(viewsets.ModelViewSet):
    """ViewSet para contactos"""
    queryset = Contacto.objects.select_related('tipo_asunto', 'estado', 'usuario').all()
    serializer_class = ContactoSerializer
    permission_classes = [AllowAny]
    # Solo usar TokenAuthentication, no SessionAuthentication para evitar CSRF en peticiones públicas
    authentication_classes = [TokenAuthentication]

    def get_serializer_class(self):
        if self.action == 'create':
            return ContactoCreateSerializer
        return ContactoSerializer
    
    def get_queryset(self):
        # Los usuarios solo pueden ver sus propios contactos, excepto staff
        if self.request.user.is_staff:
            return self.queryset
        elif self.request.user.is_authenticated:
            return self.queryset.filter(usuario=self.request.user)
        else:
            # Para usuarios anónimos, devolver queryset vacío (solo pueden crear)
            return self.queryset.none()

class SuscripcionViewSet(viewsets.ModelViewSet):
    """ViewSet para suscripciones"""
    queryset = Suscripcion.objects.select_related('usuario').all()
    serializer_class = SuscripcionSerializer
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SuscripcionCreateSerializer
        return SuscripcionSerializer
    
    def get_queryset(self):
        # Los usuarios solo pueden ver sus propias suscripciones, excepto staff
        if self.request.user.is_staff:
            return self.queryset
        elif self.request.user.is_authenticated:
            return self.queryset.filter(usuario=self.request.user)
        else:
            # Para usuarios anónimos, devolver queryset vacío (solo pueden crear)
            return self.queryset.none()
    
    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """Desactivar suscripción"""
        suscripcion = self.get_object()
        suscripcion.activa = False
        suscripcion.save()
        return Response({'message': 'Suscripción desactivada'})

# Views de compatibilidad para el frontend existente
class ContactMessageCreateView(generics.CreateAPIView):
    """Vista de compatibilidad para crear mensajes de contacto"""
    queryset = Contacto.objects.all()
    serializer_class = ContactMessageLegacySerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        # Crear usuario anónimo si no está autenticado
        if not self.request.user.is_authenticated:
            # Para el frontend existente, crear un contacto requiere autenticación
            # o implementar lógica para usuarios anónimos
            pass

@api_view(['POST'])
@permission_classes([AllowAny])
def subscribe(request):
    """Endpoint de compatibilidad para suscripciones"""
    if not request.user.is_authenticated:
        return Response({'error': 'Autenticación requerida'}, status=status.HTTP_401_UNAUTHORIZED)
    
    serializer = SuscripcionCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        email = serializer.validated_data['email']
        suscripcion, created = Suscripcion.objects.get_or_create(
            email=email,
            defaults={
                'nombre': serializer.validated_data.get('nombre', ''),
                'usuario': request.user
            }
        )
        if created:
            return Response({'message': 'Suscripción exitosa'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Ya estás suscrito'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def unsubscribe(request):
    """Endpoint de compatibilidad para desuscripciones"""
    email = request.data.get('email')
    if email:
        try:
            suscripcion = Suscripcion.objects.get(email=email)
            suscripcion.activa = False
            suscripcion.save()
            return Response({'message': 'Desuscripción exitosa'})
        except Suscripcion.DoesNotExist:
            return Response({'error': 'Email no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'error': 'Email requerido'}, status=status.HTTP_400_BAD_REQUEST)
