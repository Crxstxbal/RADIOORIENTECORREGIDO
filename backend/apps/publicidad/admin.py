from django.contrib import admin
from django.utils.html import format_html
from .models import Publicidad, PublicidadWeb, PublicidadRadial

# Sección: Modelos existentes
class PublicidadWebInline(admin.StackedInline):
    model = PublicidadWeb
    extra = 0
    fields = ('ubicacion', 'impresiones', 'clics', 'costo_por_dia')

class PublicidadRadialInline(admin.StackedInline):
    model = PublicidadRadial
    extra = 0
    fields = ('horario', 'duracion_segundos', 'valor_por_segundo')

@admin.register(Publicidad)
class PublicidadAdmin(admin.ModelAdmin):
    list_display = ['nombre_cliente', 'tipo', 'fecha_inicio', 'fecha_fin', 'activo', 'costo_total_display']
    list_filter = ['tipo', 'activo', 'fecha_inicio']
    search_fields = ['nombre_cliente', 'descripcion']
    date_hierarchy = 'fecha_inicio'
    list_editable = ['activo']
    
    def get_inlines(self, request, obj):
        if obj and obj.tipo == 'WEB':
            return [PublicidadWebInline]
        elif obj and obj.tipo == 'RADIAL':
            return [PublicidadRadialInline]
        return []
    
    def costo_total_display(self, obj):
        if obj.costo_total:
            return f"${obj.costo_total:,.2f}"
        return "-"
    costo_total_display.short_description = 'Costo Total'
    costo_total_display.admin_order_field = 'costo_total'

@admin.register(PublicidadWeb)
class PublicidadWebAdmin(admin.ModelAdmin):
    list_display = ['publicidad', 'ubicacion', 'impresiones', 'clics', 'costo_por_dia_display']
    list_filter = ['ubicacion']
    search_fields = ['publicidad__nombre_cliente']
    
    def costo_por_dia_display(self, obj):
        return f"${obj.costo_por_dia:,.2f}" if obj.costo_por_dia else "-"
    costo_por_dia_display.short_description = 'Costo/Día'

@admin.register(PublicidadRadial)
class PublicidadRadialAdmin(admin.ModelAdmin):
    list_display = ['publicidad', 'horario', 'duracion_segundos', 'valor_por_segundo_display']
    list_filter = ['horario']
    search_fields = ['publicidad__nombre_cliente']
    
    def valor_por_segundo_display(self, obj):
        return f"${obj.valor_por_segundo:,.4f}" if obj.valor_por_segundo else "-"
    valor_por_segundo_display.short_description = 'Valor x Segundo'
