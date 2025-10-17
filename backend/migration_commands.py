#!/usr/bin/env python
"""
Script con comandos para ejecutar la migración completa
"""
import os
import subprocess
import sys

def run_command(command, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"\n🔄 {description}")
    print(f"Ejecutando: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Completado")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Ejecutar todos los comandos de migración"""
    print("🚀 INICIANDO MIGRACIÓN COMPLETA A SQLITE NORMALIZADO")
    print("=" * 60)
    
    commands = [
        # 1. Limpiar migraciones existentes (opcional)
        ("find . -path '*/migrations/*.py' -not -name '__init__.py' -delete", 
         "Limpiando migraciones existentes"),
        
        ("find . -path '*/migrations/*.pyc' -delete", 
         "Limpiando archivos .pyc de migraciones"),
        
        # 2. Crear nuevas migraciones
        ("python manage.py makemigrations apps.ubicacion", 
         "Creando migraciones para ubicación"),
        
        ("python manage.py makemigrations apps.users", 
         "Creando migraciones para usuarios"),
        
        ("python manage.py makemigrations apps.radio", 
         "Creando migraciones para radio"),
        
        ("python manage.py makemigrations apps.blog", 
         "Creando migraciones para blog"),
        
        ("python manage.py makemigrations apps.contact", 
         "Creando migraciones para contacto"),
        
        ("python manage.py makemigrations apps.emergente", 
         "Creando migraciones para emergente"),
        
        ("python manage.py makemigrations apps.publicidad", 
         "Creando migraciones para publicidad"),
        
        # 3. Aplicar migraciones
        ("python manage.py migrate", 
         "Aplicando todas las migraciones"),
        
        # 4. Migrar datos
        ("python migrate_data.py", 
         "Migrando datos iniciales"),
        
        # 5. Crear superusuario (opcional)
        # ("python manage.py createsuperuser --noinput --email admin@radiooriente.com --username admin", 
        #  "Creando superusuario"),
        
        # 6. Recopilar archivos estáticos
        ("python manage.py collectstatic --noinput", 
         "Recopilando archivos estáticos"),
    ]
    
    success_count = 0
    total_commands = len(commands)
    
    for command, description in commands:
        if run_command(command, description):
            success_count += 1
        else:
            print(f"\n⚠️  Comando falló, pero continuando...")
    
    print("\n" + "=" * 60)
    print(f"📊 RESUMEN: {success_count}/{total_commands} comandos ejecutados exitosamente")
    
    if success_count == total_commands:
        print("🎉 ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. Configurar USE_SQLITE=True en .env (ya está por defecto)")
        print("2. Ejecutar: python manage.py runserver")
        print("3. Probar los endpoints en: http://localhost:8000")
        print("4. La base de datos SQLite se creará automáticamente")
    else:
        print("⚠️  Algunos comandos fallaron. Revisar errores arriba.")
    
    print("\n🔗 ENDPOINTS DISPONIBLES:")
    print("- API Principal: http://localhost:8000/")
    print("- Admin: http://localhost:8000/admin/")
    print("- Auth: http://localhost:8000/api/auth/")
    print("- Radio: http://localhost:8000/api/radio/")
    print("- Blog: http://localhost:8000/api/blog/")
    print("- Contacto: http://localhost:8000/api/contact/")
    print("- Emergentes: http://localhost:8000/api/emergentes/")
    print("- Ubicación: http://localhost:8000/api/ubicacion/")
    print("- Publicidad: http://localhost:8000/api/publicidad/")

if __name__ == '__main__':
    main()
