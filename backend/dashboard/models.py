from django.db import models

class Region(models.Model):
    """Regiones de Chile"""
    nombre = models.CharField(max_length=100, unique=True)
    codigo_iso = models.CharField(max_length=10, blank=True, null=True)
    orden = models.PositiveIntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'region'
        verbose_name = 'Región'
        verbose_name_plural = 'Regiones'
        ordering = ['orden', 'nombre']
