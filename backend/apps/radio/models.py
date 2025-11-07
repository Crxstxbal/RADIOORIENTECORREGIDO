from django.db import models
from django.conf import settings

class EstacionRadio(models.Model):
    """Estación de radio normalizada"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    stream_url = models.URLField(max_length=500, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    listeners_count = models.IntegerField(default=0)
    activo = models.BooleanField(default=True, verbose_name='En el aire', 
                              help_text='Indica si la estación está transmitiendo actualmente')

    class Meta:
        db_table = 'estacion_radio'
        verbose_name = 'Estación de Radio'
        verbose_name_plural = 'Estaciones de Radio'

    def __str__(self):
        return self.nombre

class GeneroMusical(models.Model):
    """Géneros musicales normalizados"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'genero_musical'
        verbose_name = 'Género Musical'
        verbose_name_plural = 'Géneros Musicales'
    
    def __str__(self):
        return self.nombre

class Conductor(models.Model):
    """Conductores de programas"""
    nombre = models.CharField(max_length=150)
    apellido = models.CharField(max_length=150)
    apodo = models.CharField(max_length=150, blank=True, null=True)
    foto_url = models.URLField(max_length=500, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    
    class Meta:
        db_table = 'conductor'
        verbose_name = 'Conductor'
        verbose_name_plural = 'Conductores'
    
    def __str__(self):
        if self.apodo:
            return f"{self.nombre} '{self.apodo}' {self.apellido}"
        return f"{self.nombre} {self.apellido}"

class Programa(models.Model):
    """Programas de radio normalizados"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    imagen_url = models.URLField(max_length=500, blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'programa'
        verbose_name = 'Programa'
        verbose_name_plural = 'Programas'
    
    def __str__(self):
        return self.nombre

class ProgramaConductor(models.Model):
    """Relación muchos a muchos entre programas y conductores"""
    programa = models.ForeignKey(Programa, on_delete=models.CASCADE, related_name='conductores')
    conductor = models.ForeignKey(Conductor, on_delete=models.CASCADE, related_name='programas')
    
    class Meta:
        db_table = 'programa_conductor'
        unique_together = ['programa', 'conductor']
        verbose_name = 'Programa-Conductor'
        verbose_name_plural = 'Programas-Conductores'
    
    def __str__(self):
        return f"{self.programa.nombre} - {self.conductor}"

class HorarioPrograma(models.Model):
    """Horarios de programas"""
    programa = models.ForeignKey(Programa, on_delete=models.CASCADE, related_name='horarios')
    dia_semana = models.IntegerField(
        choices=[
            (0, 'Domingo'), (1, 'Lunes'), (2, 'Martes'), (3, 'Miércoles'),
            (4, 'Jueves'), (5, 'Viernes'), (6, 'Sábado')
        ]
    )
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'horario_programa'
        ordering = ['dia_semana', 'hora_inicio']
        verbose_name = 'Horario de Programa'
        verbose_name_plural = 'Horarios de Programas'
    
    def __str__(self):
        days = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
        day_name = days[self.dia_semana]
        return f"{self.programa.nombre} - {day_name} {self.hora_inicio}-{self.hora_fin}"
