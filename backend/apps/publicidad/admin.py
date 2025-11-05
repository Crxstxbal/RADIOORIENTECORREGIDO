from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Publicidad, PublicidadWeb, PublicidadRadial,
    EspacioPublicitario, SolicitudPublicidad, ItemSolicitud, CreatividadPublicitaria
)

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

# Sección: Nuevos modelos de autoservicio
class ItemSolicitudInline(admin.TabularInline):
    model = ItemSolicitud
    extra = 0
    fields = ('espacio', 'fecha_inicio', 'fecha_fin', 'precio_dia', 'subtotal_display')
    readonly_fields = ('subtotal_display',)
    
    def subtotal_display(self, obj):
        return f"${obj.subtotal:,.2f}" if obj.subtotal else "-"
    subtotal_display.short_description = 'Subtotal'

class CreatividadPublicitariaInline(admin.StackedInline):
    model = CreatividadPublicitaria
    extra = 0
    fields = ('archivo', 'valido', 'razon_invalidez', 'fecha_subida')
    readonly_fields = ('valido', 'razon_invalidez', 'fecha_subida')

@admin.register(EspacioPublicitario)
class EspacioPublicitarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ubicacion', 'dimensiones', 'precio_por_dia_display', 'activo')
    list_filter = ('ubicacion', 'activo')
    search_fields = ('nombre', 'codigo', 'descripcion')
    list_editable = ('activo',)
    
    def dimensiones(self, obj):
        return f"{obj.ancho_px} × {obj.alto_px} px"
    dimensiones.short_description = 'Dimensiones'
    
    def precio_por_dia_display(self, obj):
        return f"${obj.precio_por_dia:,.2f}" if obj.precio_por_dia else "-"
    precio_por_dia_display.short_description = 'Precio/Día'

@admin.register(SolicitudPublicidad)
class SolicitudPublicidadAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_cliente', 'email', 'estado', 'fecha_creacion', 'monto_estimado_display')
    list_filter = ('estado', 'canal')
    search_fields = ('nombre_cliente', 'email', 'telefono')
    inlines = [ItemSolicitudInline]
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'usuario')
    date_hierarchy = 'fecha_creacion'
    
    def monto_estimado_display(self, obj):
        return f"${obj.monto_estimado:,.2f}" if obj.monto_estimado else "-"
    monto_estimado_display.short_description = 'Monto Estimado'
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Solo si es nuevo
            obj.usuario = request.user
        super().save_model(request, obj, form, change)

@admin.register(ItemSolicitud)
class ItemSolicitudAdmin(admin.ModelAdmin):
    list_display = ('id', 'solicitud_link', 'espacio', 'rango_fechas', 'subtotal_display')
    list_filter = ('espacio',)
    search_fields = ('solicitud__nombre_cliente', 'espacio__nombre')
    inlines = [CreatividadPublicitariaInline]
    
    def solicitud_link(self, obj):
        url = f'/admin/publicidad/solicitudpublicidad/{obj.solicitud.id}/change/'
        return format_html('<a href="{}">{}</a>', url, f'Solicitud #{obj.solicitud.id}')
    solicitud_link.short_description = 'Solicitud'
    
    def rango_fechas(self, obj):
        return f"{obj.fecha_inicio} al {obj.fecha_fin}"
    rango_fechas.short_description = 'Período'
    
    def subtotal_display(self, obj):
        return f"${obj.subtotal:,.2f}" if obj.subtotal else "-"
    subtotal_display.short_description = 'Subtotal'

@admin.register(CreatividadPublicitaria)
class CreatividadPublicitariaAdmin(admin.ModelAdmin):
    list_display = ('id', 'item_link', 'archivo_thumbnail', 'valido', 'fecha_subida')
    list_filter = ('valido',)
    readonly_fields = ('fecha_subida', 'ancho_px_detectado', 'alto_px_detectado', 'formato_detectado')
    
    def item_link(self, obj):
        url = f'/admin/publicidad/itemsolicitud/{obj.item.id}/change/'
        return format_html('<a href="{}">{}</a>', url, f'Item #{obj.item.id}')
    item_link.short_description = 'Ítem'
    
    def archivo_thumbnail(self, obj):
        if obj.archivo:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="max-height: 50px;" /></a>',
                obj.archivo.url, obj.archivo.url
            )
        return "-"
    archivo_thumbnail.short_description = 'Vista Previa'
    archivo_thumbnail.allow_tags = True
