# 🚀 Migración a PostgreSQL - Radio Oriente FM

## 📋 Resumen de Cambios

Esta migración transforma la base de datos de **SQLite no normalizada** a **PostgreSQL completamente normalizada** manteniendo toda la funcionalidad existente y agregando nuevas características.

### ✨ Mejoras Implementadas

- ✅ **Base de datos normalizada** con llaves foráneas apropiadas
- ✅ **Estructura PostgreSQL** siguiendo mejores prácticas
- ✅ **Modelos Django optimizados** con relaciones correctas
- ✅ **APIs RESTful completas** con ViewSets y serializers
- ✅ **Compatibilidad con frontend existente** mediante endpoints legacy
- ✅ **Sistema de ubicación normalizado** (País → Ciudad → Comuna)
- ✅ **Gestión de publicidad** web y radial
- ✅ **Sistema de estados y tipos** para contactos y bandas

## 🗂️ Nueva Estructura de Apps

```
apps/
├── ubicacion/          # 🌍 Países, ciudades, comunas
├── users/             # 👥 Usuarios (actualizado)
├── radio/             # 📻 Estación, programas, conductores, géneros
├── blog/              # 📝 Artículos y categorías
├── contact/           # 📞 Contactos, suscripciones, tipos, estados
├── emergente/         # 🎸 Bandas emergentes e integrantes
└── publicidad/        # 📺 Publicidad web y radial
```

## 🔄 Proceso de Migración

### Prerrequisitos

1. **PostgreSQL instalado y corriendo**
2. **Base de datos creada**: `radio_oriente_db`
3. **Usuario PostgreSQL** con permisos

### Paso 1: Configurar Entorno

```bash
# Copiar archivo de configuración
cp env.example .env

# Editar variables de base de datos
# DB_NAME=radio_oriente_db
# DB_USER=postgres
# DB_PASSWORD=tu_password
# DB_HOST=localhost
# DB_PORT=5432
```

### Paso 2: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 3: Ejecutar Migración Automática

```bash
# Opción 1: Script automático (recomendado)
python migration_commands.py

# Opción 2: Comandos manuales
python manage.py makemigrations
python manage.py migrate
python migrate_data.py
python manage.py collectstatic --noinput
```

### Paso 4: Verificar Migración

```bash
python manage.py runserver
```

Visitar: http://localhost:8000/

## 🔗 Nuevos Endpoints

### APIs Normalizadas

```
📍 Ubicación:
- GET /api/ubicacion/paises/
- GET /api/ubicacion/ciudades/
- GET /api/ubicacion/comunas/

📻 Radio:
- GET /api/radio/api/estaciones/
- GET /api/radio/api/generos/
- GET /api/radio/api/conductores/
- GET /api/radio/api/programas/
- GET /api/radio/api/horarios/

📝 Blog:
- GET /api/blog/api/categorias/
- GET /api/blog/api/articulos/

📞 Contacto:
- GET /api/contact/api/tipos-asunto/
- GET /api/contact/api/estados/
- GET /api/contact/api/contactos/
- GET /api/contact/api/suscripciones/

🎸 Emergentes:
- GET /api/emergentes/api/integrantes/
- GET /api/emergentes/api/bandas/

📺 Publicidad:
- GET /api/publicidad/publicidades/
```

### APIs de Compatibilidad (Frontend Existente)

```
- GET /api/radio/station/
- GET /api/radio/programs/
- GET /api/blog/posts/
- POST /api/contact/message/
- POST /api/contact/subscribe/
- GET /api/emergentes/
```

## 📊 Mapeo de Datos

### Usuarios
```
SQLite (Anterior)          →  PostgreSQL (Nuevo)
usuarios.correo           →  usuario.email
usuarios.usuario          →  usuario.username
usuarios.nombre           →  usuario.first_name + last_name
```

### Programas
```
SQLite (Anterior)          →  PostgreSQL (Nuevo)
programacion.conductor    →  programa_conductor (tabla relación)
programacion.dia_semana   →  horario_programa.dia_semana
programacion.hora_*       →  horario_programa.hora_*
```

### Bandas Emergentes
```
SQLite (Anterior)          →  PostgreSQL (Nuevo)
bandas.integrantes        →  banda_integrante (tabla relación)
bandas.links              →  banda_link (tabla separada)
bandas.ciudad             →  comuna.ciudad (normalizado)
bandas.genero             →  genero_musical (tabla separada)
```

## 🛠️ Características Técnicas

### Modelos Normalizados

- **Llaves foráneas** en todas las relaciones
- **Índices optimizados** para consultas frecuentes
- **Constraints de integridad** en base de datos
- **Relaciones many-to-many** apropiadas
- **Campos de auditoría** (fechas de creación/modificación)

### Serializers Avanzados

- **Serializers anidados** para relaciones
- **Campos calculados** y propiedades
- **Validaciones personalizadas**
- **Serializers de compatibilidad** para frontend existente

### ViewSets y Permisos

- **ViewSets RESTful** completos
- **Permisos granulares** por usuario
- **Filtros y búsquedas** avanzadas
- **Acciones personalizadas** (@action)

## 🔒 Seguridad

- **Autenticación por token** mantenida
- **Permisos por usuario** implementados
- **Validaciones de entrada** reforzadas
- **Sanitización de datos** mejorada

## 📈 Performance

- **Consultas optimizadas** con select_related/prefetch_related
- **Índices de base de datos** en campos críticos
- **Paginación automática** en listas grandes
- **Cache de consultas** frecuentes

## 🧪 Testing

```bash
# Ejecutar tests
python manage.py test

# Verificar cobertura
coverage run --source='.' manage.py test
coverage report
```

## 🚨 Troubleshooting

### Error: "relation does not exist"
```bash
python manage.py migrate --run-syncdb
```

### Error: "authentication failed"
- Verificar credenciales PostgreSQL en `.env`
- Confirmar que PostgreSQL esté corriendo

### Error: "port already in use"
```bash
python manage.py runserver 8001
```

### Datos no aparecen
```bash
python migrate_data.py
```

## 📞 Soporte

Si encuentras problemas durante la migración:

1. **Revisar logs** de Django y PostgreSQL
2. **Verificar configuración** de `.env`
3. **Ejecutar comandos** paso a paso manualmente
4. **Consultar documentación** de Django y PostgreSQL

## 🎯 Próximos Pasos

1. **Probar todas las funcionalidades** del frontend
2. **Migrar datos reales** de producción
3. **Configurar backup automático** de PostgreSQL
4. **Optimizar consultas** según uso real
5. **Implementar monitoring** de performance

---

**¡Migración completada exitosamente! 🎉**

La aplicación ahora cuenta con una base de datos normalizada, APIs RESTful completas y mantiene total compatibilidad con el frontend existente.
