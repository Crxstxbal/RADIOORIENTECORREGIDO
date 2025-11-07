from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal

# ==========================
# Modelos existentes
# ==========================

class Publicidad(models.Model):
    """Publicidad base normalizada"""
    TIPO_CHOICES = [
        ('WEB', 'Web'),
        ('RADIAL', 'Radial'),
    ]
    
    nombre_cliente = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activo = models.BooleanField(default=True)
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.00'))])
    archivo_media = models.URLField(max_length=500, blank=True, null=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='publicidades')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'publicidad'
        verbose_name = 'Publicidad'
        verbose_name_plural = 'Publicidades'
        indexes = [
            models.Index(fields=['usuario']),
            models.Index(fields=['tipo']),
            models.Index(fields=['activo']),
            models.Index(fields=['fecha_inicio', 'fecha_fin']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(fecha_fin__gte=models.F('fecha_inicio')),
                name='publicidad_fechas_validas'
            )
        ]
    
    def __str__(self):
        return f"{self.nombre_cliente} - {self.get_tipo_display()}"

class PublicidadWeb(models.Model):
    """Publicidad web específica"""
    UBICACION_CHOICES = [
        ('banner_superior', 'Banner Superior'),
        ('lateral', 'Lateral'),
        ('footer', 'Footer'),
    ]
    
    publicidad = models.OneToOneField(Publicidad, on_delete=models.CASCADE, related_name='web_config')
    ubicacion = models.CharField(max_length=50, choices=UBICACION_CHOICES)
    formato = models.CharField(max_length=50, blank=True, null=True)
    url_destino = models.URLField(max_length=500, blank=True, null=True)
    impresiones = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    clics = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    costo_por_dia = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.00'))])
    
    class Meta:
        db_table = 'publicidad_web'
        verbose_name = 'Publicidad Web'
        verbose_name_plural = 'Publicidades Web'
    
    def __str__(self):
        return f"{self.publicidad.nombre_cliente} - {self.get_ubicacion_display()}"

class PublicidadRadial(models.Model):
    """Publicidad radial específica"""
    publicidad = models.OneToOneField(Publicidad, on_delete=models.CASCADE, related_name='radial_config')
    horario = models.ForeignKey('radio.HorarioPrograma', on_delete=models.CASCADE, related_name='publicidades')
    duracion_segundos = models.IntegerField(validators=[MinValueValidator(1)])
    valor_por_segundo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.00'))])
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.00'))])
    
    class Meta:
        db_table = 'publicidad_radial'
        verbose_name = 'Publicidad Radial'
        verbose_name_plural = 'Publicidades Radiales'
        indexes = [
            models.Index(fields=['horario']),
        ]
    
    def __str__(self):
        return f"{self.publicidad.nombre_cliente} - {self.horario}"
