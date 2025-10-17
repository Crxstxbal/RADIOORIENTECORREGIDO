from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.text import slugify
from .models import Categoria, Articulo
from .serializers import (
    CategoriaSerializer, ArticuloSerializer, ArticuloListSerializer, 
    ArticuloCreateSerializer, BlogPostLegacySerializer
)

# ViewSets normalizados
class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para categorías (solo lectura)"""
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ArticuloViewSet(viewsets.ModelViewSet):
    """ViewSet para artículos"""
    queryset = Articulo.objects.select_related('autor', 'categoria').filter(publicado=True)
    serializer_class = ArticuloSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ArticuloListSerializer
        elif self.action == 'create':
            return ArticuloCreateSerializer
        return ArticuloSerializer
    
    @action(detail=False, methods=['get'])
    def destacados(self, request):
        """Obtener artículos destacados"""
        destacados = self.queryset.filter(destacado=True)[:5]
        serializer = ArticuloListSerializer(destacados, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_categoria(self, request):
        """Obtener artículos por categoría"""
        categoria_id = request.query_params.get('categoria_id')
        if categoria_id:
            articulos = self.queryset.filter(categoria_id=categoria_id)
            serializer = ArticuloListSerializer(articulos, many=True)
            return Response(serializer.data)
        return Response([])

# Views de compatibilidad para el frontend existente
class BlogPostListView(generics.ListCreateAPIView):
    """Vista de compatibilidad para artículos"""
    queryset = Articulo.objects.filter(publicado=True)
    serializer_class = BlogPostLegacySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Buscar o crear categoría por defecto
        categoria_default, created = Categoria.objects.get_or_create(
            nombre='General',
            defaults={'descripcion': 'Categoría general'}
        )
        serializer.save(
            autor=self.request.user,
            categoria=categoria_default
        )

class BlogPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista de compatibilidad para detalle de artículo"""
    queryset = Articulo.objects.filter(publicado=True)
    serializer_class = BlogPostLegacySerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticatedOrReadOnly]
