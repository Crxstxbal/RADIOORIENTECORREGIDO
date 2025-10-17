from rest_framework import serializers
from .models import TipoAsunto, Estado, Contacto, Suscripcion

class TipoAsuntoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoAsunto
        fields = ['id', 'nombre']

class EstadoSerializer(serializers.ModelSerializer):
    tipo_entidad_display = serializers.CharField(source='get_tipo_entidad_display', read_only=True)
    
    class Meta:
        model = Estado
        fields = ['id', 'nombre', 'descripcion', 'tipo_entidad', 'tipo_entidad_display']

class ContactoSerializer(serializers.ModelSerializer):
    tipo_asunto_nombre = serializers.CharField(source='tipo_asunto.nombre', read_only=True)
    estado_nombre = serializers.CharField(source='estado.nombre', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.full_name', read_only=True)
    respondido_por_nombre = serializers.CharField(source='respondido_por.full_name', read_only=True)
    
    class Meta:
        model = Contacto
        fields = [
            'id', 'nombre', 'email', 'telefono', 'tipo_asunto', 'tipo_asunto_nombre',
            'mensaje', 'usuario', 'usuario_nombre', 'estado', 'estado_nombre',
            'fecha_envio', 'fecha_respuesta', 'respondido_por', 'respondido_por_nombre'
        ]
        read_only_fields = ('fecha_envio', 'fecha_respuesta', 'respondido_por')

class ContactoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear contactos"""
    
    class Meta:
        model = Contacto
        fields = ['nombre', 'email', 'telefono', 'tipo_asunto', 'mensaje']
    
    def create(self, validated_data):
        # Asignar usuario actual y estado por defecto
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['usuario'] = request.user
        else:
            # Para usuarios anónimos, usar el usuario admin o crear uno por defecto
            from django.contrib.auth import get_user_model
            User = get_user_model()
            admin_user = User.objects.filter(is_staff=True).first()
            if admin_user:
                validated_data['usuario'] = admin_user
        
        # Buscar estado "Pendiente" para contactos (primer estado por defecto)
        estado_pendiente = Estado.objects.filter(
            tipo_entidad='contacto'
        ).first()  # Toma el primer estado disponible
        
        if estado_pendiente:
            validated_data['estado'] = estado_pendiente
        
        return super().create(validated_data)

class SuscripcionSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.full_name', read_only=True)
    
    class Meta:
        model = Suscripcion
        fields = [
            'id', 'email', 'nombre', 'activa', 'fecha_suscripcion',
            'fecha_baja', 'usuario', 'usuario_nombre'
        ]
        read_only_fields = ('fecha_suscripcion', 'fecha_baja', 'token_unsuscribe')

class SuscripcionCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear suscripciones"""
    
    class Meta:
        model = Suscripcion
        fields = ['email', 'nombre']
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['usuario'] = request.user
        else:
            # Para usuarios anónimos, usar el usuario admin o crear uno por defecto
            from django.contrib.auth import get_user_model
            User = get_user_model()
            admin_user = User.objects.filter(is_staff=True).first()
            if admin_user:
                validated_data['usuario'] = admin_user
        return super().create(validated_data)

# Serializers de compatibilidad para el frontend existente
class ContactMessageLegacySerializer(serializers.ModelSerializer):
    """Serializer para mantener compatibilidad con el frontend existente"""
    correo = serializers.CharField(source='email', read_only=True)
    asunto = serializers.CharField(source='tipo_asunto.nombre', read_only=True)
    estado = serializers.CharField(source='estado.nombre', read_only=True)
    
    class Meta:
        model = Contacto
        fields = ['id', 'nombre', 'correo', 'telefono', 'asunto', 'mensaje', 'fecha_envio', 'estado']

class SubscriptionLegacySerializer(serializers.ModelSerializer):
    """Serializer para mantener compatibilidad con el frontend existente"""
    correo = serializers.CharField(source='email', read_only=True)
    
    class Meta:
        model = Suscripcion
        fields = ['id', 'correo', 'nombre', 'activa', 'fecha_suscripcion']
