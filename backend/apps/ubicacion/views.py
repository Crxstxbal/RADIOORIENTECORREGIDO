from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Pais, Ciudad, Comuna
from .serializers import PaisSerializer, CiudadSerializer, ComunaSerializer, ComunaDetailSerializer

class PaisViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para países (solo lectura)"""
    queryset = Pais.objects.all()
    serializer_class = PaisSerializer
    permission_classes = [permissions.AllowAny]

class CiudadViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para ciudades (solo lectura)"""
    queryset = Ciudad.objects.select_related('pais').all()
    serializer_class = CiudadSerializer
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['get'])
    def por_pais(self, request):
        """Obtener ciudades por país"""
        pais_id = request.query_params.get('pais_id')
        if pais_id:
            ciudades = self.queryset.filter(pais_id=pais_id)
            serializer = self.get_serializer(ciudades, many=True)
            return Response(serializer.data)
        return Response([])

class ComunaViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para comunas (solo lectura)"""
    queryset = Comuna.objects.select_related('ciudad__pais').all()
    serializer_class = ComunaSerializer
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['get'])
    def por_ciudad(self, request):
        """Obtener comunas por ciudad"""
        ciudad_id = request.query_params.get('ciudad_id')
        if ciudad_id:
            comunas = self.queryset.filter(ciudad_id=ciudad_id)
            serializer = ComunaDetailSerializer(comunas, many=True)
            return Response(serializer.data)
        return Response([])
