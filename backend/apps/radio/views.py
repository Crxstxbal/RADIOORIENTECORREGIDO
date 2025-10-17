from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .models import EstacionRadio, GeneroMusical, Conductor, Programa, ProgramaConductor, HorarioPrograma
from .serializers import (
    EstacionRadioSerializer, GeneroMusicalSerializer, ConductorSerializer,
    ProgramaSerializer, ProgramaDetailSerializer, ProgramLegacySerializer,
    HorarioProgramaSerializer, ProgramaConductorSerializer
)

# ViewSets normalizados
class EstacionRadioViewSet(viewsets.ModelViewSet):
    """ViewSet para estaciones de radio"""
    queryset = EstacionRadio.objects.all()
    serializer_class = EstacionRadioSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class GeneroMusicalViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para géneros musicales (solo lectura)"""
    queryset = GeneroMusical.objects.all()
    serializer_class = GeneroMusicalSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ConductorViewSet(viewsets.ModelViewSet):
    """ViewSet para conductores"""
    queryset = Conductor.objects.filter(activo=True)
    serializer_class = ConductorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ProgramaViewSet(viewsets.ModelViewSet):
    """ViewSet para programas"""
    queryset = Programa.objects.filter(activo=True).prefetch_related('conductores', 'horarios')
    serializer_class = ProgramaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProgramaDetailSerializer
        return ProgramaSerializer
    
    @action(detail=False, methods=['get'])
    def por_dia(self, request):
        """Obtener programas por día de la semana"""
        dia = request.query_params.get('dia')
        if dia is not None:
            try:
                dia = int(dia)
                programas = self.queryset.filter(horarios__dia_semana=dia, horarios__activo=True).distinct()
                serializer = self.get_serializer(programas, many=True)
                return Response(serializer.data)
            except ValueError:
                pass
        return Response([])

class HorarioProgramaViewSet(viewsets.ModelViewSet):
    """ViewSet para horarios de programas"""
    queryset = HorarioPrograma.objects.select_related('programa').filter(activo=True)
    serializer_class = HorarioProgramaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

# Views de compatibilidad para el frontend existente
class RadioStationView(generics.RetrieveUpdateAPIView):
    """Vista de compatibilidad para estación de radio"""
    queryset = EstacionRadio.objects.all()
    serializer_class = EstacionRadioSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self):
        station, created = EstacionRadio.objects.get_or_create(
            id=1,
            defaults={
                'nombre': 'Radio Oriente FM',
                'descripcion': 'La mejor música y noticias de oriente',
                'stream_url': 'https://sonic-us.fhost.cl/8126/stream',
            }
        )
        return station

class ProgramListView(generics.ListCreateAPIView):
    """Vista de compatibilidad para programas"""
    queryset = Programa.objects.filter(activo=True)
    serializer_class = ProgramLegacySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ProgramDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista de compatibilidad para detalle de programa"""
    queryset = Programa.objects.all()
    serializer_class = ProgramLegacySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_current_song(request):
    """Actualizar canción actual (funcionalidad futura)"""
    try:
        station = EstacionRadio.objects.get(id=1)
        # Funcionalidad para implementar después
        return Response({'message': 'Funcionalidad en desarrollo'})
    except EstacionRadio.DoesNotExist:
        return Response({'error': 'Estación no encontrada'}, status=status.HTTP_404_NOT_FOUND)
