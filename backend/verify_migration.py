#!/usr/bin/env python
"""
Script para verificar que la migración se completó correctamente
"""
import os
import sys
import django
import requests
from django.db import connection
from django.core.management import execute_from_command_line

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'radio_oriente.settings')
django.setup()

def test_database_connection():
    """Probar conexión a la base de datos"""
    print("🔌 Probando conexión a SQLite...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT sqlite_version();")
            version = cursor.fetchone()[0]
            print(f"  ✅ Conectado a SQLite versión: {version}")
            return True
    except Exception as e:
        print(f"  ❌ Error de conexión: {str(e)}")
        return False

def test_models():
    """Probar que todos los modelos funcionan correctamente"""
    print("\n📊 Verificando modelos...")
    
    try:
        # Importar todos los modelos
        from apps.users.models import User
        from apps.ubicacion.models import Pais, Ciudad, Comuna
        from apps.radio.models import EstacionRadio, GeneroMusical, Conductor, Programa
        from apps.blog.models import Categoria, Articulo
        from apps.contact.models import TipoAsunto, Estado, Contacto, Suscripcion
        from apps.emergente.models import Integrante, BandaEmergente
        from apps.publicidad.models import Publicidad
        
        # Contar registros en cada modelo
        models_data = [
            (User, "Usuarios"),
            (Pais, "Países"),
            (Ciudad, "Ciudades"),
            (Comuna, "Comunas"),
            (EstacionRadio, "Estaciones de Radio"),
            (GeneroMusical, "Géneros Musicales"),
            (Conductor, "Conductores"),
            (Programa, "Programas"),
            (Categoria, "Categorías"),
            (Articulo, "Artículos"),
            (TipoAsunto, "Tipos de Asunto"),
            (Estado, "Estados"),
            (Contacto, "Contactos"),
            (Suscripcion, "Suscripciones"),
            (Integrante, "Integrantes"),
            (BandaEmergente, "Bandas Emergentes"),
            (Publicidad, "Publicidades")
        ]
        
        all_good = True
        for model, name in models_data:
            try:
                count = model.objects.count()
                print(f"  ✅ {name}: {count} registros")
            except Exception as e:
                print(f"  ❌ Error en {name}: {str(e)}")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"  ❌ Error importando modelos: {str(e)}")
        return False

def test_relationships():
    """Probar que las relaciones funcionan correctamente"""
    print("\n🔗 Verificando relaciones...")
    
    try:
        from apps.users.models import User
        from apps.radio.models import Programa, Conductor, ProgramaConductor
        from apps.ubicacion.models import Comuna
        
        # Probar relación Usuario
        if User.objects.exists():
            user = User.objects.first()
            print(f"  ✅ Usuario: {user.full_name} ({user.email})")
        
        # Probar relación Programa-Conductor
        if ProgramaConductor.objects.exists():
            pc = ProgramaConductor.objects.first()
            print(f"  ✅ Relación Programa-Conductor: {pc.programa.nombre} - {pc.conductor}")
        
        # Probar relación Comuna-Ciudad-País
        if Comuna.objects.exists():
            comuna = Comuna.objects.select_related('ciudad__pais').first()
            print(f"  ✅ Ubicación: {comuna.nombre}, {comuna.ciudad.nombre}, {comuna.ciudad.pais.nombre}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error verificando relaciones: {str(e)}")
        return False

def test_api_endpoints():
    """Probar que los endpoints API funcionan"""
    print("\n🌐 Verificando endpoints API...")
    
    base_url = "http://localhost:8000"
    endpoints = [
        "/",
        "/api/ubicacion/paises/",
        "/api/radio/api/generos/",
        "/api/blog/api/categorias/",
        "/api/contact/api/tipos-asunto/",
        # Endpoints de compatibilidad
        "/api/radio/station/",
        "/api/radio/programs/",
        "/api/blog/posts/"
    ]
    
    server_running = False
    try:
        response = requests.get(base_url, timeout=5)
        server_running = True
        print(f"  ✅ Servidor corriendo en {base_url}")
    except:
        print(f"  ⚠️  Servidor no está corriendo en {base_url}")
        print("     Ejecuta: python manage.py runserver")
        return False
    
    if server_running:
        success_count = 0
        for endpoint in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    print(f"  ✅ {endpoint} - OK")
                    success_count += 1
                else:
                    print(f"  ⚠️  {endpoint} - Status {response.status_code}")
            except Exception as e:
                print(f"  ❌ {endpoint} - Error: {str(e)}")
        
        print(f"\n📊 APIs funcionando: {success_count}/{len(endpoints)}")
        return success_count == len(endpoints)
    
    return False

def test_admin_panel():
    """Verificar que el panel de administración funciona"""
    print("\n👨‍💼 Verificando panel de administración...")
    
    try:
        base_url = "http://localhost:8000"
        response = requests.get(f"{base_url}/admin/", timeout=5)
        if response.status_code == 200:
            print("  ✅ Panel de administración accesible")
            return True
        else:
            print(f"  ⚠️  Panel admin status: {response.status_code}")
            return False
    except:
        print("  ⚠️  No se pudo acceder al panel de administración")
        return False

def run_verification():
    """Ejecutar todas las verificaciones"""
    print("🔍 VERIFICACIÓN POST-MIGRACIÓN")
    print("=" * 50)
    
    tests = [
        ("Conexión a Base de Datos", test_database_connection),
        ("Modelos Django", test_models),
        ("Relaciones", test_relationships),
        ("Endpoints API", test_api_endpoints),
        ("Panel Admin", test_admin_panel)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
    
    # Resumen final
    print("\n" + "=" * 50)
    print("📋 RESUMEN DE VERIFICACIÓN")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Resultado: {passed}/{len(tests)} verificaciones exitosas")
    
    if passed == len(tests):
        print("\n🎉 ¡MIGRACIÓN VERIFICADA EXITOSAMENTE!")
        print("\n✨ Todo está funcionando correctamente:")
        print("   • Base de datos SQLite normalizada conectada")
        print("   • Modelos normalizados funcionando")
        print("   • Relaciones establecidas correctamente")
        print("   • APIs RESTful operativas")
        print("   • Panel de administración accesible")
        print("\n🚀 La aplicación está lista para usar!")
    else:
        print("\n⚠️  Algunas verificaciones fallaron.")
        print("   Revisa los errores arriba y ejecuta los comandos necesarios.")
    
    return passed == len(tests)

if __name__ == '__main__':
    success = run_verification()
    sys.exit(0 if success else 1)
