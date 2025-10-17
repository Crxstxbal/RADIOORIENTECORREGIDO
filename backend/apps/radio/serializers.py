from rest_framework import serializers
from .models import EstacionRadio, GeneroMusical, Conductor, Programa, ProgramaConductor, HorarioPrograma

class EstacionRadioSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstacionRadio
        fields = '__all__'

class GeneroMusicalSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneroMusical
        fields = ['id', 'nombre', 'descripcion']

class ConductorSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Conductor
        fields = ['id', 'nombre', 'apellido', 'apodo', 'foto_url', 'email', 'telefono', 'activo', 'nombre_completo']
    
    def get_nombre_completo(self, obj):
        return str(obj)

class HorarioProgramaSerializer(serializers.ModelSerializer):
    dia_semana_display = serializers.CharField(source='get_dia_semana_display', read_only=True)
    
    class Meta:
        model = HorarioPrograma
        fields = ['id', 'programa', 'dia_semana', 'dia_semana_display', 'hora_inicio', 'hora_fin', 'activo']

class ProgramaConductorSerializer(serializers.ModelSerializer):
    conductor_nombre = serializers.CharField(source='conductor.__str__', read_only=True)
    
    class Meta:
        model = ProgramaConductor
        fields = ['id', 'programa', 'conductor', 'conductor_nombre']

class ProgramaSerializer(serializers.ModelSerializer):
    conductores = ProgramaConductorSerializer(many=True, read_only=True)
    horarios = HorarioProgramaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Programa
        fields = ['id', 'nombre', 'descripcion', 'imagen_url', 'activo', 'conductores', 'horarios']

class ProgramaDetailSerializer(serializers.ModelSerializer):
    conductores = ConductorSerializer(source='conductores.conductor', many=True, read_only=True)
    horarios = HorarioProgramaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Programa
        fields = ['id', 'nombre', 'descripcion', 'imagen_url', 'activo', 'conductores', 'horarios']

# Serializers de compatibilidad para el frontend existente
class ProgramLegacySerializer(serializers.ModelSerializer):
    """Serializer para mantener compatibilidad con el frontend existente"""
    nombre_programa = serializers.CharField(source='nombre', read_only=True)
    conductor = serializers.SerializerMethodField()
    
    class Meta:
        model = Programa
        fields = ['id', 'nombre_programa', 'descripcion', 'conductor', 'activo']
    
    def get_conductor(self, obj):
        conductores = obj.conductores.all()
        if conductores:
            return ', '.join([str(pc.conductor) for pc in conductores])
        return None
