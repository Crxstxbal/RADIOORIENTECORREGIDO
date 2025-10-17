from django.contrib import admin
from .models import Categoria, Articulo

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'categoria', 'publicado', 'destacado', 'fecha_publicacion')
    list_filter = ('publicado', 'destacado', 'categoria', 'fecha_publicacion')
    list_editable = ('publicado', 'destacado')
    search_fields = ('titulo', 'contenido')
    readonly_fields = ('slug', 'fecha_creacion')
    prepopulated_fields = {'slug': ('titulo',)}
