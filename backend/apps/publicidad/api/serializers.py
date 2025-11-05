from rest_framework import serializers
from apps.publicidad.models import (
    EspacioPublicitario, 
    SolicitudPublicidad, 
    ItemSolicitud, 
    CreatividadPublicitaria
)

class CreatividadPublicitariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreatividadPublicitaria
        fields = ['id', 'item', 'archivo', 'fecha_subida', 'valido']
        read_only_fields = ['fecha_subida', 'valido']

class ItemSolicitudSerializer(serializers.ModelSerializer):
    creatividad = CreatividadPublicitariaSerializer(read_only=True)
    espacio_nombre = serializers.CharField(source='espacio.nombre', read_only=True)
    espacio_dimensiones = serializers.SerializerMethodField()
    espacio_precio = serializers.DecimalField(
        source='espacio.precio_por_dia', 
        max_digits=10, 
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = ItemSolicitud
        fields = [
            'id', 'solicitud', 'espacio', 'espacio_nombre', 'espacio_dimensiones',
            'espacio_precio', 'fecha_inicio', 'fecha_fin', 'creatividad'
        ]

    def get_espacio_dimensiones(self, obj):
        return f"{obj.espacio.ancho_px} x {obj.espario.alto_px} px"

class SolicitudPublicidadSerializer(serializers.ModelSerializer):
    items = ItemSolicitudSerializer(many=True, read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)

    class Meta:
        model = SolicitudPublicidad
        fields = [
            'id', 'usuario', 'usuario_nombre', 'fecha_creacion', 'fecha_modificacion',
            'estado', 'estado_display', 'comentarios', 'items', 'total'
        ]
        read_only_fields = ['usuario', 'fecha_creacion', 'fecha_modificacion', 'estado']

    def create(self, validated_data):
        # El usuario se establece automáticamente
        return SolicitudPublicidad.objects.create(**validated_data)

class EspacioPublicitarioSerializer(serializers.ModelSerializer):
    dimensiones = serializers.SerializerMethodField()
    formato = serializers.SerializerMethodField()

    class Meta:
        model = EspacioPublicitario
        fields = [
            'id', 'nombre', 'descripcion', 'ancho_px', 'alto_px', 'dimensiones',
            'formato', 'precio_por_dia', 'activo', 'ubicacion', 'formato_archivo'
        ]

    def get_dimensiones(self, obj):
        return f"{obj.ancho_px} x {obj.alto_px} px"

    def get_formato(self, obj):
        return obj.get_formato_archivo_display()
