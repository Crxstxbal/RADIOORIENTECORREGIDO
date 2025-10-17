from rest_framework import serializers
from .models import Publicidad, PublicidadWeb, PublicidadRadial

class PublicidadWebSerializer(serializers.ModelSerializer):
    ubicacion_display = serializers.CharField(source='get_ubicacion_display', read_only=True)
    
    class Meta:
        model = PublicidadWeb
        fields = [
            'id', 'ubicacion', 'ubicacion_display', 'formato', 'url_destino',
            'impresiones', 'clics', 'costo_por_dia'
        ]

class PublicidadRadialSerializer(serializers.ModelSerializer):
    programa_nombre = serializers.CharField(source='programa.nombre', read_only=True)
    horario_info = serializers.CharField(source='horario.__str__', read_only=True)
    
    class Meta:
        model = PublicidadRadial
        fields = [
            'id', 'programa', 'programa_nombre', 'horario', 'horario_info',
            'duracion_segundos', 'valor_por_segundo', 'costo_total'
        ]

class PublicidadSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.full_name', read_only=True)
    web_config = PublicidadWebSerializer(read_only=True)
    radial_config = PublicidadRadialSerializer(read_only=True)
    
    class Meta:
        model = Publicidad
        fields = [
            'id', 'nombre_cliente', 'descripcion', 'tipo', 'tipo_display',
            'fecha_inicio', 'fecha_fin', 'activo', 'costo_total', 'archivo_media',
            'usuario', 'usuario_nombre', 'fecha_creacion', 'web_config', 'radial_config'
        ]
        read_only_fields = ('fecha_creacion',)

class PublicidadCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear publicidades"""
    web_config = PublicidadWebSerializer(required=False)
    radial_config = PublicidadRadialSerializer(required=False)
    
    class Meta:
        model = Publicidad
        fields = [
            'nombre_cliente', 'descripcion', 'tipo', 'fecha_inicio', 'fecha_fin',
            'activo', 'costo_total', 'archivo_media', 'web_config', 'radial_config'
        ]
    
    def create(self, validated_data):
        web_config_data = validated_data.pop('web_config', None)
        radial_config_data = validated_data.pop('radial_config', None)
        
        validated_data['usuario'] = self.context['request'].user
        publicidad = super().create(validated_data)
        
        if publicidad.tipo == 'WEB' and web_config_data:
            PublicidadWeb.objects.create(publicidad=publicidad, **web_config_data)
        elif publicidad.tipo == 'RADIAL' and radial_config_data:
            PublicidadRadial.objects.create(publicidad=publicidad, **radial_config_data)
        
        return publicidad

class PublicidadListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listas"""
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = Publicidad
        fields = [
            'id', 'nombre_cliente', 'tipo', 'tipo_display', 'fecha_inicio',
            'fecha_fin', 'activo', 'costo_total'
        ]
