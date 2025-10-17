#!/usr/bin/env python
"""
Script para migrar datos de SQLite a PostgreSQL con estructura normalizada
"""
import os
import sys
import django
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.hashers import make_password

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'radio_oriente.settings')
django.setup()

def migrate_data():
    """Migrar datos de SQLite a PostgreSQL"""
    print("🚀 Iniciando migración de datos...")
    
    try:
        # Importar modelos después de configurar Django
        from apps.users.models import User
        from apps.ubicacion.models import Pais, Ciudad, Comuna
        from apps.radio.models import EstacionRadio, GeneroMusical, Conductor, Programa, HorarioPrograma, ProgramaConductor
        from apps.blog.models import Categoria, Articulo
        from apps.contact.models import TipoAsunto, Estado, Contacto, Suscripcion
        from apps.emergente.models import Integrante, BandaEmergente, BandaLink, BandaIntegrante
        
        with transaction.atomic():
            print("📍 Creando datos de ubicación...")
            create_location_data()
            
            print("👥 Creando usuarios por defecto...")
            create_default_users()
            
            print("📻 Creando datos de radio...")
            create_radio_data()
            
            print("📝 Creando categorías y estados...")
            create_categories_and_states()
            
            print("✅ Migración completada exitosamente!")
            
    except Exception as e:
        print(f"❌ Error durante la migración: {str(e)}")
        raise

def create_location_data():
    """Crear datos de ubicación básicos"""
    from apps.ubicacion.models import Pais, Ciudad, Comuna
    
    # Crear países
    venezuela, _ = Pais.objects.get_or_create(nombre='Venezuela')
    
    # Crear ciudades principales de Venezuela
    ciudades_data = [
        'Caracas', 'Maracaibo', 'Valencia', 'Barquisimeto', 'Maracay',
        'Ciudad Guayana', 'Barcelona', 'Maturín', 'Puerto La Cruz',
        'Petare', 'Turmero', 'Ciudad Bolívar', 'Mérida', 'San Cristóbal'
    ]
    
    ciudades = []
    for ciudad_nombre in ciudades_data:
        ciudad, created = Ciudad.objects.get_or_create(
            nombre=ciudad_nombre,
            pais=venezuela
        )
        ciudades.append(ciudad)
        if created:
            print(f"  ✓ Ciudad creada: {ciudad_nombre}")
    
    # Crear algunas comunas para Caracas como ejemplo
    caracas = Ciudad.objects.get(nombre='Caracas', pais=venezuela)
    comunas_caracas = [
        'Libertador', 'Chacao', 'Baruta', 'Sucre', 'El Hatillo'
    ]
    
    for comuna_nombre in comunas_caracas:
        comuna, created = Comuna.objects.get_or_create(
            nombre=comuna_nombre,
            ciudad=caracas
        )
        if created:
            print(f"  ✓ Comuna creada: {comuna_nombre}, Caracas")

def create_default_users():
    """Crear usuarios por defecto"""
    from apps.users.models import User
    
    # Crear superusuario por defecto
    if not User.objects.filter(email='admin@radiooriente.com').exists():
        admin_user = User.objects.create_user(
            email='admin@radiooriente.com',
            username='admin',
            first_name='Administrador',
            last_name='Sistema',
            password='admin123'
        )
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        print("  ✓ Usuario administrador creado: admin@radiooriente.com")
    
    # Crear usuario de prueba
    if not User.objects.filter(email='test@radiooriente.com').exists():
        User.objects.create_user(
            email='test@radiooriente.com',
            username='testuser',
            first_name='Usuario',
            last_name='Prueba',
            password='test123'
        )
        print("  ✓ Usuario de prueba creado: test@radiooriente.com")

def create_radio_data():
    """Crear datos básicos de radio"""
    from apps.radio.models import EstacionRadio, GeneroMusical, Conductor, Programa, HorarioPrograma, ProgramaConductor
    
    # Crear estación de radio
    estacion, created = EstacionRadio.objects.get_or_create(
        id=1,
        defaults={
            'nombre': 'Radio Oriente FM',
            'descripcion': 'La mejor música y noticias de oriente',
            'stream_url': 'https://sonic-us.fhost.cl/8126/stream',
            'telefono': '+58-123-456-7890',
            'email': 'info@radiooriente.com',
            'direccion': 'Caracas, Venezuela'
        }
    )
    if created:
        print("  ✓ Estación de radio creada")
    
    # Crear géneros musicales
    generos = [
        ('Rock', 'Música rock en todas sus variantes'),
        ('Pop', 'Música pop contemporánea'),
        ('Salsa', 'Música salsa y tropical'),
        ('Reggaeton', 'Música urbana y reggaeton'),
        ('Balada', 'Baladas románticas'),
        ('Merengue', 'Música merengue'),
        ('Bachata', 'Música bachata'),
        ('Jazz', 'Música jazz'),
        ('Blues', 'Música blues'),
        ('Electrónica', 'Música electrónica'),
        ('Alternativo', 'Música alternativa'),
        ('Indie', 'Música independiente')
    ]
    
    for nombre, descripcion in generos:
        genero, created = GeneroMusical.objects.get_or_create(
            nombre=nombre,
            defaults={'descripcion': descripcion}
        )
        if created:
            print(f"  ✓ Género musical creado: {nombre}")
    
    # Crear conductores
    conductores_data = [
        ('Carlos', 'Rodríguez', 'El Locutor', 'carlos@radiooriente.com'),
        ('María', 'González', 'La Voz', 'maria@radiooriente.com'),
        ('José', 'Martínez', 'El DJ', 'jose@radiooriente.com'),
        ('Ana', 'López', None, 'ana@radiooriente.com')
    ]
    
    conductores = []
    for nombre, apellido, apodo, email in conductores_data:
        conductor, created = Conductor.objects.get_or_create(
            email=email,
            defaults={
                'nombre': nombre,
                'apellido': apellido,
                'apodo': apodo,
                'telefono': '+58-123-456-789' + str(len(conductores))
            }
        )
        conductores.append(conductor)
        if created:
            print(f"  ✓ Conductor creado: {nombre} {apellido}")
    
    # Crear programas
    programas_data = [
        ('Buenos Días Oriente', 'Programa matutino con noticias y música'),
        ('Música sin Fronteras', 'Los mejores éxitos internacionales'),
        ('Noches de Salsa', 'Programa nocturno de música tropical'),
        ('Rock en Español', 'Lo mejor del rock en nuestro idioma'),
        ('Domingos Familiares', 'Programa familiar para toda la familia')
    ]
    
    programas = []
    for nombre, descripcion in programas_data:
        programa, created = Programa.objects.get_or_create(
            nombre=nombre,
            defaults={'descripcion': descripcion}
        )
        programas.append(programa)
        if created:
            print(f"  ✓ Programa creado: {nombre}")
    
    # Asignar conductores a programas
    if conductores and programas:
        # Buenos Días Oriente - Carlos y María
        ProgramaConductor.objects.get_or_create(
            programa=programas[0],
            conductor=conductores[0]
        )
        ProgramaConductor.objects.get_or_create(
            programa=programas[0],
            conductor=conductores[1]
        )
        
        # Música sin Fronteras - José
        ProgramaConductor.objects.get_or_create(
            programa=programas[1],
            conductor=conductores[2]
        )
        
        # Noches de Salsa - Ana
        ProgramaConductor.objects.get_or_create(
            programa=programas[2],
            conductor=conductores[3]
        )
    
    # Crear horarios
    horarios_data = [
        (programas[0], 1, '06:00', '10:00'),  # Buenos Días Oriente - Lunes
        (programas[0], 2, '06:00', '10:00'),  # Buenos Días Oriente - Martes
        (programas[0], 3, '06:00', '10:00'),  # Buenos Días Oriente - Miércoles
        (programas[0], 4, '06:00', '10:00'),  # Buenos Días Oriente - Jueves
        (programas[0], 5, '06:00', '10:00'),  # Buenos Días Oriente - Viernes
        (programas[1], 1, '14:00', '18:00'),  # Música sin Fronteras - Lunes
        (programas[2], 5, '20:00', '23:00'),  # Noches de Salsa - Viernes
        (programas[3], 6, '15:00', '18:00'),  # Rock en Español - Sábado
        (programas[4], 0, '10:00', '14:00'),  # Domingos Familiares - Domingo
    ]
    
    for programa, dia, hora_inicio, hora_fin in horarios_data:
        if programa:  # Verificar que el programa existe
            horario, created = HorarioPrograma.objects.get_or_create(
                programa=programa,
                dia_semana=dia,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin
            )
            if created:
                print(f"  ✓ Horario creado: {programa.nombre} - {['Dom','Lun','Mar','Mié','Jue','Vie','Sáb'][dia]}")

def create_categories_and_states():
    """Crear categorías y estados básicos"""
    from apps.blog.models import Categoria
    from apps.contact.models import TipoAsunto, Estado
    
    # Crear categorías para blog
    categorias = [
        ('Noticias', 'Noticias y actualidad'),
        ('Música', 'Artículos sobre música'),
        ('Entretenimiento', 'Contenido de entretenimiento'),
        ('Deportes', 'Noticias deportivas'),
        ('Cultura', 'Eventos culturales'),
        ('General', 'Artículos generales')
    ]
    
    for nombre, descripcion in categorias:
        categoria, created = Categoria.objects.get_or_create(
            nombre=nombre,
            defaults={'descripcion': descripcion}
        )
        if created:
            print(f"  ✓ Categoría creada: {nombre}")
    
    # Crear tipos de asunto para contactos
    tipos_asunto = [
        'Consulta General',
        'Programación',
        'Publicidad',
        'Soporte Técnico',
        'Sugerencias',
        'Quejas',
        'Otro'
    ]
    
    for nombre in tipos_asunto:
        tipo, created = TipoAsunto.objects.get_or_create(nombre=nombre)
        if created:
            print(f"  ✓ Tipo de asunto creado: {nombre}")
    
    # Crear estados para contactos
    estados_contacto = [
        ('Nuevo', 'Contacto recién recibido', 'contacto'),
        ('En Proceso', 'Contacto siendo atendido', 'contacto'),
        ('Resuelto', 'Contacto resuelto satisfactoriamente', 'contacto'),
        ('Cerrado', 'Contacto cerrado', 'contacto')
    ]
    
    for nombre, descripcion, tipo_entidad in estados_contacto:
        estado, created = Estado.objects.get_or_create(
            nombre=nombre,
            tipo_entidad=tipo_entidad,
            defaults={'descripcion': descripcion}
        )
        if created:
            print(f"  ✓ Estado de contacto creado: {nombre}")
    
    # Crear estados para bandas emergentes
    estados_banda = [
        ('Pendiente', 'Banda pendiente de revisión', 'banda'),
        ('En Revisión', 'Banda siendo evaluada', 'banda'),
        ('Aprobada', 'Banda aprobada para participar', 'banda'),
        ('Rechazada', 'Banda no cumple requisitos', 'banda'),
        ('Contactada', 'Banda contactada para seguimiento', 'banda')
    ]
    
    for nombre, descripcion, tipo_entidad in estados_banda:
        estado, created = Estado.objects.get_or_create(
            nombre=nombre,
            tipo_entidad=tipo_entidad,
            defaults={'descripcion': descripcion}
        )
        if created:
            print(f"  ✓ Estado de banda creado: {nombre}")

if __name__ == '__main__':
    migrate_data()
