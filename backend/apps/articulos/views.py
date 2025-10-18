from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.text import slugify
from .models import Categoria, Articulo, ComentarioArticulo
from .serializers import (
    CategoriaSerializer, ArticuloSerializer, ArticuloListSerializer, 
    ArticuloCreateSerializer, BlogPostLegacySerializer, ComentarioArticuloSerializer
)

# ViewSets normalizados
class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para categorías (solo lectura)"""
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

class ArticuloViewSet(viewsets.ModelViewSet):
    """ViewSet para artículos con soporte multimedia"""
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
    
    def retrieve(self, request, *args, **kwargs):
        """Incrementa vistas al obtener un artículo"""
        instance = self.get_object()
        instance.vistas += 1
        instance.save(update_fields=['vistas'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def destacados(self, request):
        """Obtener artículos destacados"""
        destacados = self.queryset.filter(destacado=True).order_by('-fecha_publicacion')[:5]
        serializer = ArticuloListSerializer(destacados, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_categoria(self, request):
        """Obtener artículos por categoría"""
        categoria_slug = request.query_params.get('categoria')
        if categoria_slug:
            articulos = self.queryset.filter(categoria__slug=categoria_slug)
            serializer = ArticuloListSerializer(articulos, many=True, context={'request': request})
            return Response(serializer.data)
        return Response([])
    
    @action(detail=False, methods=['get'])
    def mas_vistos(self, request):
        """Obtener artículos más vistos"""
        mas_vistos = self.queryset.order_by('-vistas')[:10]
        serializer = ArticuloListSerializer(mas_vistos, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def comentarios(self, request, slug=None):
        """Obtener comentarios de un artículo"""
        articulo = self.get_object()
        comentarios = articulo.comentarios.filter(activo=True)
        serializer = ComentarioArticuloSerializer(comentarios, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def comentar(self, request, slug=None):
        """Agregar comentario a un artículo"""
        articulo = self.get_object()
        serializer = ComentarioArticuloSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(articulo=articulo)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
