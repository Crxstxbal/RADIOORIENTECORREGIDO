#!/usr/bin/env python
"""
Script para poblar datos iniciales en la base de datos normalizada de Radio Oriente
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'radio_oriente.settings')
django.setup()

from apps.ubicacion.models import Pais, Ciudad, Comuna
from apps.radio.models import EstacionRadio, GeneroMusical, Conductor, Programa
from apps.contact.models import TipoAsunto, Estado
from apps.blog.models import Categoria

def create_ubicacion_data():
    """Crear datos de ubicación básicos"""
    print("Creando datos de ubicación...")
    
    # Crear Chile
    chile, created = Pais.objects.get_or_create(
        nombre="Chile"
    )
    if created:
        print("✓ País Chile creado")
    
    # Crear algunas ciudades principales
    ciudades_data = [
        'Santiago',
        'Valparaíso',
        'Concepción',
        'La Serena',
        'Antofagasta',
    ]
    
    for ciudad_nombre in ciudades_data:
        ciudad, created = Ciudad.objects.get_or_create(
            nombre=ciudad_nombre,
            pais=chile
        )
        if created:
            print(f"✓ Ciudad {ciudad.nombre} creada")
    
    # Crear algunas comunas para Santiago
    santiago = Ciudad.objects.get(nombre='Santiago')
    comunas_santiago = [
        'Santiago Centro', 'Las Condes', 'Providencia', 'Ñuñoa', 
        'La Florida', 'Maipú', 'Puente Alto', 'San Bernardo'
    ]
    
    for comuna_nombre in comunas_santiago:
        comuna, created = Comuna.objects.get_or_create(
            nombre=comuna_nombre,
            ciudad=santiago
        )
        if created:
            print(f"✓ Comuna {comuna.nombre} creada")

def create_radio_data():
    """Crear datos básicos de radio"""
    print("Creando datos de radio...")
    
    # Crear estación de radio principal
    estacion, created = EstacionRadio.objects.get_or_create(
        nombre="Radio Oriente FM",
        defaults={
            'descripcion': 'La radio que conecta con tu música favorita',
            'stream_url': 'http://streaming.radiooriente.com/live',
            'telefono': '+56 2 2345 6789',
            'email': 'contacto@radiooriente.com',
            'direccion': 'Av. Providencia 1234, Santiago, Chile',
            'listeners_count': 0
        }
    )
    if created:
        print("✓ Estación Radio Oriente FM creada")
    
    # Crear géneros musicales
    generos = [
        {'nombre': 'Rock', 'descripcion': 'Música rock nacional e internacional'},
        {'nombre': 'Pop', 'descripcion': 'Los éxitos más populares'},
        {'nombre': 'Reggaeton', 'descripcion': 'El ritmo urbano que mueve'},
        {'nombre': 'Baladas', 'descripcion': 'Las mejores baladas románticas'},
        {'nombre': 'Cumbia', 'descripcion': 'Cumbia chilena y latinoamericana'},
        {'nombre': 'Electrónica', 'descripcion': 'Música electrónica y dance'},
        {'nombre': 'Hip Hop', 'descripcion': 'Hip hop y rap nacional e internacional'},
        {'nombre': 'Indie', 'descripcion': 'Música independiente y alternativa'},
    ]
    
    for genero_data in generos:
        genero, created = GeneroMusical.objects.get_or_create(
            nombre=genero_data['nombre'],
            defaults={'descripcion': genero_data['descripcion']}
        )
        if created:
            print(f"✓ Género {genero.nombre} creado")
    
    # Crear algunos conductores
    conductores_data = [
        {
            'nombre': 'Carlos',
            'apellido': 'Rodríguez',
            'apodo': 'El Carlitos',
            'email': 'carlos@radiooriente.com'
        },
        {
            'nombre': 'María',
            'apellido': 'González',
            'apodo': 'Mary Music',
            'email': 'maria@radiooriente.com'
        },
        {
            'nombre': 'Diego',
            'apellido': 'Silva',
            'apodo': 'DJ Diego',
            'email': 'diego@radiooriente.com'
        }
    ]
    
    for conductor_data in conductores_data:
        conductor, created = Conductor.objects.get_or_create(
            email=conductor_data['email'],
            defaults=conductor_data
        )
        if created:
            print(f"✓ Conductor {conductor.nombre} {conductor.apellido} creado")
    
    # Crear algunos programas
    programas_data = [
        {
            'nombre': 'Buenos Días Oriente',
            'descripcion': 'El programa matutino que te despierta con la mejor música'
        },
        {
            'nombre': 'Tarde de Éxitos',
            'descripcion': 'Los hits más populares en tu tarde'
        },
        {
            'nombre': 'Noche Urbana',
            'descripcion': 'Reggaeton y música urbana para la noche'
        },
        {
            'nombre': 'Rock en Español',
            'descripcion': 'El mejor rock nacional e internacional'
        }
    ]
    
    for programa_data in programas_data:
        programa, created = Programa.objects.get_or_create(
            nombre=programa_data['nombre'],
            defaults={'descripcion': programa_data['descripcion']}
        )
        if created:
            print(f"✓ Programa {programa.nombre} creado")

def create_contact_data():
    """Crear datos básicos de contacto"""
    print("Creando datos de contacto...")
    
    # Crear tipos de asunto
    tipos_asunto = [
        'Consulta General',
        'Publicidad',
        'Programación',
        'Técnico',
        'Reclamo',
        'Felicitaciones',
    ]
    
    for tipo_nombre in tipos_asunto:
        tipo, created = TipoAsunto.objects.get_or_create(
            nombre=tipo_nombre
        )
        if created:
            print(f"✓ Tipo de asunto {tipo.nombre} creado")
    
    # Crear estados para contactos
    estados_contacto = [
        {'nombre': 'Pendiente', 'descripcion': 'Mensaje recibido, pendiente de revisión', 'tipo_entidad': 'contacto'},
        {'nombre': 'En Proceso', 'descripcion': 'Mensaje en proceso de respuesta', 'tipo_entidad': 'contacto'},
        {'nombre': 'Resuelto', 'descripcion': 'Mensaje resuelto satisfactoriamente', 'tipo_entidad': 'contacto'},
        {'nombre': 'Cerrado', 'descripcion': 'Caso cerrado', 'tipo_entidad': 'contacto'},
    ]
    
    for estado_data in estados_contacto:
        estado, created = Estado.objects.get_or_create(
            nombre=estado_data['nombre'],
            tipo_entidad=estado_data['tipo_entidad'],
            defaults={'descripcion': estado_data['descripcion']}
        )
        if created:
            print(f"✓ Estado {estado.nombre} para contactos creado")
    
    # Crear estados para bandas
    estados_banda = [
        {'nombre': 'Recibida', 'descripcion': 'Solicitud recibida', 'tipo_entidad': 'banda'},
        {'nombre': 'En Revisión', 'descripcion': 'Solicitud en proceso de revisión', 'tipo_entidad': 'banda'},
        {'nombre': 'Aprobada', 'descripcion': 'Solicitud aprobada', 'tipo_entidad': 'banda'},
        {'nombre': 'Rechazada', 'descripcion': 'Solicitud rechazada', 'tipo_entidad': 'banda'},
    ]
    
    for estado_data in estados_banda:
        estado, created = Estado.objects.get_or_create(
            nombre=estado_data['nombre'],
            tipo_entidad=estado_data['tipo_entidad'],
            defaults={'descripcion': estado_data['descripcion']}
        )
        if created:
            print(f"✓ Estado {estado.nombre} para bandas creado")

def create_blog_data():
    """Crear categorías básicas para el blog"""
    print("Creando categorías de blog...")
    
    categorias = [
        {'nombre': 'Noticias', 'descripcion': 'Noticias de la radio y el mundo musical'},
        {'nombre': 'Entrevistas', 'descripcion': 'Entrevistas a artistas y personalidades'},
        {'nombre': 'Eventos', 'descripcion': 'Eventos y conciertos'},
        {'nombre': 'Música', 'descripcion': 'Artículos sobre música y artistas'},
        {'nombre': 'Tecnología', 'descripcion': 'Tecnología y radio'},
        {'nombre': 'Cultura', 'descripcion': 'Cultura y entretenimiento'},
    ]
    
    for categoria_data in categorias:
        categoria, created = Categoria.objects.get_or_create(
            nombre=categoria_data['nombre'],
            defaults={'descripcion': categoria_data['descripcion']}
        )
        if created:
            print(f"✓ Categoría {categoria.nombre} creada")

def main():
    """Función principal"""
    print("🚀 Iniciando población de datos iniciales...")
    print("=" * 50)
    
    try:
        create_ubicacion_data()
        print()
        create_radio_data()
        print()
        create_contact_data()
        print()
        create_blog_data()
        print()
        print("=" * 50)
        print("✅ ¡Datos iniciales creados exitosamente!")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error al crear datos iniciales: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
