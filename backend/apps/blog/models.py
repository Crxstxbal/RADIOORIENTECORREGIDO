from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Categoria(models.Model):
    """Categorías de artículos normalizadas"""
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'categoria'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
    
    def __str__(self):
        return self.nombre

class Articulo(models.Model):
    """Artículos de blog normalizados"""
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    contenido = models.TextField()
    resumen = models.TextField(blank=True, null=True)
    imagen_url = models.URLField(max_length=500, blank=True, null=True)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='articulos')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='articulos')
    publicado = models.BooleanField(default=False)
    destacado = models.BooleanField(default=False)
    fecha_publicacion = models.DateTimeField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'articulo'
        ordering = ['-fecha_publicacion', '-fecha_creacion']
        verbose_name = 'Artículo'
        verbose_name_plural = 'Artículos'
        indexes = [
            models.Index(fields=['publicado']),
            models.Index(fields=['slug']),
            models.Index(fields=['autor']),
            models.Index(fields=['categoria']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo
