from django.contrib import admin
from .models import Categoria, Articulo, ComentarioArticulo

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'descripcion')
    search_fields = ('nombre',)
    prepopulated_fields = {'slug': ('nombre',)}

@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'categoria', 'publicado', 'destacado', 'fecha_publicacion', 'vistas', 'tiene_multimedia')
    list_filter = ('publicado', 'destacado', 'categoria', 'fecha_publicacion', 'fecha_creacion')
    list_editable = ('publicado', 'destacado')
    search_fields = ('titulo', 'contenido', 'resumen')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'vistas', 'imagen_destacada')
    prepopulated_fields = {'slug': ('titulo',)}
    
    fieldsets = (
        ('Información básica', {
            'fields': ('titulo', 'slug', 'autor', 'categoria')
        }),
        ('Contenido', {
            'fields': ('resumen', 'contenido')
        }),
        ('Multimedia', {
            'fields': ('imagen_portada', 'imagen_thumbnail', 'imagen_url', 'imagen_destacada', 'video_url', 'archivo_adjunto'),
            'description': 'Imagen Banner (horizontal) para modal, Imagen Thumbnail (cuadrada) para tarjetas de lista, o URL externa.'
        }),
        ('Estado y visibilidad', {
            'fields': ('publicado', 'destacado', 'fecha_publicacion')
        }),
        ('Metadatos', {
            'fields': ('vistas', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ComentarioArticulo)
class ComentarioArticuloAdmin(admin.ModelAdmin):
    list_display = ('articulo', 'autor', 'contenido_corto', 'fecha_creacion', 'activo')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('contenido', 'autor__username', 'articulo__titulo')
    list_editable = ('activo',)
    readonly_fields = ('fecha_creacion',)
    
    def contenido_corto(self, obj):
        return obj.contenido[:50] + '...' if len(obj.contenido) > 50 else obj.contenido
    contenido_corto.short_description = 'Comentario'
