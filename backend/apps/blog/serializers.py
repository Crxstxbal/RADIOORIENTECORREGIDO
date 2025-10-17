from rest_framework import serializers
from .models import Categoria, Articulo

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion']

class ArticuloSerializer(serializers.ModelSerializer):
    autor_nombre = serializers.CharField(source='autor.full_name', read_only=True)
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    
    class Meta:
        model = Articulo
        fields = [
            'id', 'titulo', 'slug', 'contenido', 'resumen', 'imagen_url',
            'autor', 'autor_nombre', 'categoria', 'categoria_nombre',
            'publicado', 'destacado', 'fecha_publicacion', 'fecha_creacion'
        ]
        read_only_fields = ('slug', 'fecha_creacion')

class ArticuloListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listas"""
    autor_nombre = serializers.CharField(source='autor.full_name', read_only=True)
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    
    class Meta:
        model = Articulo
        fields = [
            'id', 'titulo', 'slug', 'resumen', 'imagen_url',
            'autor_nombre', 'categoria_nombre', 'publicado', 'destacado',
            'fecha_publicacion', 'fecha_creacion'
        ]

class ArticuloCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear artículos"""
    
    class Meta:
        model = Articulo
        fields = [
            'titulo', 'contenido', 'resumen', 'imagen_url',
            'categoria', 'publicado', 'destacado', 'fecha_publicacion'
        ]
    
    def create(self, validated_data):
        validated_data['autor'] = self.context['request'].user
        return super().create(validated_data)

# Serializers de compatibilidad para el frontend existente
class BlogPostLegacySerializer(serializers.ModelSerializer):
    """Serializer para mantener compatibilidad con el frontend existente"""
    autor_id = serializers.IntegerField(source='autor.id', read_only=True)
    autor_nombre = serializers.CharField(source='autor.full_name', read_only=True)
    categoria = serializers.CharField(source='categoria.nombre', read_only=True)
    
    class Meta:
        model = Articulo
        fields = [
            'id', 'titulo', 'contenido', 'resumen', 'imagen_url',
            'autor_id', 'autor_nombre', 'categoria', 'publicado',
            'fecha_publicacion', 'fecha_creacion'
        ]
