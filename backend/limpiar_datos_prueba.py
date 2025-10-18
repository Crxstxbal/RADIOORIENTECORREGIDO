"""
Script para eliminar datos de prueba de artículos
Ejecutar: python limpiar_datos_prueba.py
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'radio_oriente.settings')
django.setup()

from apps.articulos.models import Articulo, Categoria, ComentarioArticulo

def limpiar_datos():
    """Elimina todos los datos de prueba de artículos"""
    
    print("🗑️  Iniciando limpieza de datos de prueba...\n")
    
    # Contar antes de eliminar
    total_articulos = Articulo.objects.count()
    total_comentarios = ComentarioArticulo.objects.count()
    total_categorias = Categoria.objects.count()
    
    print(f"📊 Estado actual:")
    print(f"   - Artículos: {total_articulos}")
    print(f"   - Comentarios: {total_comentarios}")
    print(f"   - Categorías: {total_categorias}\n")
    
    # Confirmar eliminación
    respuesta = input("⚠️  ¿Estás seguro de eliminar TODOS los datos? (escribe 'SI' para confirmar): ")
    
    if respuesta.upper() != 'SI':
        print("❌ Operación cancelada.")
        return
    
    print("\n🔄 Eliminando datos...\n")
    
    # Eliminar comentarios primero (por integridad referencial)
    if total_comentarios > 0:
        ComentarioArticulo.objects.all().delete()
        print(f"✅ {total_comentarios} comentarios eliminados")
    
    # Eliminar artículos
    if total_articulos > 0:
        # Eliminar archivos multimedia asociados
        for articulo in Articulo.objects.all():
            if articulo.imagen_portada:
                try:
                    articulo.imagen_portada.delete(save=False)
                except:
                    pass
            if articulo.archivo_adjunto:
                try:
                    articulo.archivo_adjunto.delete(save=False)
                except:
                    pass
        
        Articulo.objects.all().delete()
        print(f"✅ {total_articulos} artículos eliminados")
    
    # Eliminar categorías (opcional - descomenta si quieres eliminar todas)
    # if total_categorias > 0:
    #     Categoria.objects.all().delete()
    #     print(f"✅ {total_categorias} categorías eliminadas")
    
    print("\n✨ ¡Limpieza completada exitosamente!")
    print("\n💡 Ahora puedes empezar a crear artículos nuevos desde el dashboard.")

if __name__ == '__main__':
    limpiar_datos()
