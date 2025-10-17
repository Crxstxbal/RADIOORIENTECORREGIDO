from django.contrib import admin
from .models import Publicidad, PublicidadWeb, PublicidadRadial

class PublicidadWebInline(admin.StackedInline):
    model = PublicidadWeb
    extra = 0

class PublicidadRadialInline(admin.StackedInline):
    model = PublicidadRadial
    extra = 0

@admin.register(Publicidad)
class PublicidadAdmin(admin.ModelAdmin):
    list_display = ['nombre_cliente', 'tipo', 'fecha_inicio', 'fecha_fin', 'activo', 'costo_total']
    list_filter = ['tipo', 'activo', 'fecha_inicio']
    search_fields = ['nombre_cliente', 'descripcion']
    date_hierarchy = 'fecha_inicio'
    
    def get_inlines(self, request, obj):
        if obj and obj.tipo == 'WEB':
            return [PublicidadWebInline]
        elif obj and obj.tipo == 'RADIAL':
            return [PublicidadRadialInline]
        return []

@admin.register(PublicidadWeb)
class PublicidadWebAdmin(admin.ModelAdmin):
    list_display = ['publicidad', 'ubicacion', 'impresiones', 'clics', 'costo_por_dia']
    list_filter = ['ubicacion']

@admin.register(PublicidadRadial)
class PublicidadRadialAdmin(admin.ModelAdmin):
    list_display = ['publicidad', 'programa', 'duracion_segundos', 'valor_por_segundo']
    list_filter = ['programa']
