# 📋 Instrucciones de Migración: Blog → Artículos

## ✅ Cambios Realizados

### 1. Nueva App `apps.articulos`
- ✅ Creada carpeta `apps/articulos/` completa
- ✅ Modelos actualizados con soporte multimedia
- ✅ Serializers, views, URLs y admin configurados
- ✅ Comentarios de artículos incluidos

### 2. Modelos Actualizados

**Modelo `Articulo`** ahora incluye:
- `imagen_portada` - ImageField para subir imágenes
- `video_url` - URLField para videos de YouTube/Vimeo
- `archivo_adjunto` - FileField para PDFs, Word, etc.
- `vistas` - Contador de visualizaciones
- `fecha_actualizacion` - Timestamp automático

### 3. Configuraciones Actualizadas
- ✅ `settings.py` - Cambiado `apps.blog` → `apps.articulos`
- ✅ `urls.py` - Rutas actualizadas a `/api/articulos/`
- ✅ `dashboard/views.py` - Imports y lógica actualizada
- ✅ Templates mejorados con campos multimedia

---

## 🚀 Pasos para Aplicar los Cambios

### Paso 1: Instalar Pillow (para imágenes)
```bash
pip install pillow
```

### Paso 2: Crear las Migraciones

**IMPORTANTE**: Como cambiamos el nombre de la app, Django creará nuevas migraciones. Los datos existentes se mantendrán porque los modelos usan `db_table` explícito.

```bash
# Crear migraciones para la nueva app
python manage.py makemigrations articulos

# Aplicar migraciones
python manage.py migrate articulos
```

### Paso 3: Eliminar la App Antigua (Opcional)

Una vez que verifiques que todo funciona:

```bash
# Eliminar migraciones antiguas de blog
python manage.py migrate blog zero --fake

# Luego puedes eliminar físicamente la carpeta
# rm -rf apps/blog  (en Linux/Mac)
# rmdir /s apps\blog  (en Windows)
```

### Paso 4: Limpiar Datos de Prueba (Opcional)

Si quieres empezar desde cero:

```bash
python limpiar_datos_prueba.py
```

### Paso 5: Crear Directorios para Media

```bash
# En el directorio backend/
mkdir media
mkdir media\articulos
mkdir media\articulos\imagenes
mkdir media\articulos\archivos
```

### Paso 6: Verificar Configuración de Media

Asegúrate que `settings.py` tenga:

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

Y que `urls.py` principal incluya (ya está configurado):

```python
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### Paso 7: Ejecutar el Servidor

```bash
python manage.py runserver
```

---

## 🎯 Probar la Funcionalidad

### 1. Acceder al Dashboard
```
http://localhost:8000/dashboard/login/
```

### 2. Ir a Artículos
```
http://localhost:8000/dashboard/articulos/
```

### 3. Crear un Artículo con Multimedia
- Click en "Nuevo Artículo"
- Llenar título, categoría, contenido
- **Subir imagen** o poner URL
- Agregar video de YouTube (opcional)
- Adjuntar archivo PDF (opcional)
- Click en "Crear Artículo"

### 4. Verificar que los Archivos se Suben
Los archivos se guardarán en:
- `media/articulos/imagenes/YYYY/MM/nombre-articulo.jpg`
- `media/articulos/archivos/YYYY/MM/documento.pdf`

---

## 📂 Estructura de Archivos Multimedia

```
backend/
├── media/
│   └── articulos/
│       ├── imagenes/
│       │   └── 2025/
│       │       └── 01/
│       │           └── mi-articulo.jpg
│       └── archivos/
│           └── 2025/
│               └── 01/
│                   └── documento.pdf
```

---

## 🔧 Configuración Adicional (Opcional)

### Limitar Tamaño de Archivos

Agrega en `settings.py`:

```python
# Tamaño máximo de archivos
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
```

### Validación de Formatos en Views

Ya implementado en `dashboard/views.py`:
- Imágenes: Cualquier formato que acepte el navegador
- Archivos: Sin restricción (puedes agregar validación)

---

## 🐛 Solución de Problemas

### Error: "No module named 'PIL'"
```bash
pip install pillow
```

### Error: "CSRF verification failed"
Asegúrate que los formularios tengan:
```html
<form method="post" enctype="multipart/form-data">
    {% csrf_token %}
```

### Los archivos no se suben
1. Verifica que el formulario tenga `enctype="multipart/form-data"`
2. Verifica que la carpeta `media/` exista y tenga permisos de escritura
3. Verifica que `MEDIA_ROOT` esté configurado correctamente

### Error: "Broken reference"
Si ves errores de referencias rotas:
1. Asegúrate de haber actualizado todos los imports
2. Ejecuta: `python manage.py check`

---

## 📊 Endpoints de API Disponibles

### Nuevos Endpoints
```
GET  /api/articulos/api/articulos/          - Lista de artículos
GET  /api/articulos/api/articulos/{slug}/   - Detalle de artículo
GET  /api/articulos/api/categorias/         - Lista de categorías
GET  /api/articulos/api/articulos/destacados/     - Artículos destacados
GET  /api/articulos/api/articulos/mas_vistos/     - Más vistos
POST /api/articulos/api/articulos/{slug}/comentar/ - Agregar comentario
```

### Endpoints Legacy (compatibilidad)
```
GET  /api/articulos/posts/       - Lista (formato antiguo)
GET  /api/articulos/posts/{id}/  - Detalle (formato antiguo)
```

---

## ✅ Checklist Final

- [ ] Pillow instalado
- [ ] Migraciones creadas y aplicadas
- [ ] Directorio `media/` creado
- [ ] Servidor funcionando sin errores
- [ ] Dashboard accesible
- [ ] Formulario de artículos muestra campos multimedia
- [ ] Subida de imagen funciona
- [ ] Subida de archivo funciona
- [ ] URLs de video se guardan correctamente
- [ ] Archivos se guardan en `media/articulos/`
- [ ] Las imágenes se muestran en el frontend (si aplica)

---

## 📝 Notas Importantes

1. **Datos Existentes**: Los datos de la tabla `articulo` se mantienen porque usamos `db_table` explícito.

2. **Carpeta `apps/blog`**: Puedes eliminarla después de verificar que todo funciona.

3. **Producción**: En producción, configura un servicio de almacenamiento cloud (AWS S3, Google Cloud Storage) para los archivos multimedia.

4. **Backups**: Haz backup de tu base de datos antes de aplicar migraciones.

5. **Performance**: Considera agregar `django-imagekit` para optimizar imágenes automáticamente.

---

## 🎉 ¡Todo Listo!

Ahora tu aplicación tiene soporte completo para:
- ✅ Subir imágenes de portada
- ✅ Videos embebidos (YouTube/Vimeo)
- ✅ Archivos adjuntos (PDF, Word, etc.)
- ✅ URLs de imágenes externas
- ✅ Sistema de comentarios
- ✅ Contador de vistas
- ✅ Artículos destacados
- ✅ Categorización mejorada

**¡A crear contenido!** 🚀
