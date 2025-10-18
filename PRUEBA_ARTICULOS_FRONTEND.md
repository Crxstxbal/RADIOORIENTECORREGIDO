# 🧪 Guía de Pruebas - Artículos Frontend

## 📋 Pre-requisitos

✅ Backend corriendo en `http://localhost:8000`  
✅ Base de datos migrada con campos multimedia  
✅ Al menos 1 artículo creado en el dashboard  

---

## 🚀 Pasos para Probar

### 1. Iniciar el Backend
```bash
cd backend
python manage.py runserver
```

**Verificar:**
- Servidor corriendo en `http://localhost:8000`
- Admin accesible en `http://localhost:8000/admin/`

### 2. Crear Artículos de Prueba

#### Opción A: Desde el Dashboard
```
http://localhost:8000/dashboard/articulos/
```
1. Click en "Nuevo Artículo"
2. Llenar los campos:
   - ✏️ Título: "Bienvenidos a Radio Oriente FM"
   - 📁 Categoría: Seleccionar una
   - 📝 Resumen: "Breve descripción del artículo"
   - 📄 Contenido: Texto completo
   - 🖼️ Subir imagen de portada (opcional)
   - 🎥 URL de video YouTube (opcional)
   - 📎 Archivo adjunto (opcional)
   - ✅ Marcar "Publicar inmediatamente"
3. Click en "Crear Artículo"

#### Opción B: Desde el Admin de Django
```
http://localhost:8000/admin/articulos/articulo/add/
```
1. Llenar todos los campos
2. Marcar "Publicado" y/o "Destacado"
3. Guardar

### 3. Iniciar el Frontend
```bash
cd frontend
npm start
```

**Verificar:**
- Frontend corriendo en `http://localhost:3000`
- No hay errores en la consola

---

## ✅ Lista de Verificación

### Página de Inicio (`/`)
- [ ] Sección "Últimos Artículos" muestra 3 artículos destacados
- [ ] Imágenes se cargan correctamente
- [ ] Fechas se muestran en formato español
- [ ] Botón "Ver todos los artículos" funciona

### Página de Artículos (`/articulos`)

#### Vista General
- [ ] Página carga sin errores
- [ ] Título "Artículos" visible
- [ ] Barra de búsqueda funcional
- [ ] Filtro de categorías funcional

#### Artículos Destacados
- [ ] Sección "Artículos Destacados" visible (si hay destacados)
- [ ] Grid con máximo 3 artículos
- [ ] Imágenes de portada se muestran correctamente
- [ ] Categorías visibles con icono
- [ ] Nombre del autor visible
- [ ] Fecha formateada correctamente

#### Lista de Artículos
- [ ] Grid de artículos regulares
- [ ] Botón "Leer más" en cada tarjeta
- [ ] Hover effect funciona
- [ ] Responsive en móviles

#### Modal de Lectura
Al hacer click en un artículo:
- [ ] Modal se abre correctamente
- [ ] Imagen destacada visible (si existe)
- [ ] Título del artículo
- [ ] Categoría con icono
- [ ] Autor y fecha
- [ ] Resumen destacado (si existe)
- [ ] Contenido completo
- [ ] **Video embebido** (si existe `video_url`)
  - [ ] YouTube se reproduce correctamente
  - [ ] Responsive (16:9)
- [ ] **Enlace de descarga** (si existe `archivo_adjunto`)
  - [ ] Click abre/descarga el archivo
  - [ ] Link funciona correctamente
- [ ] Botón cerrar (×) funciona
- [ ] Click fuera del modal lo cierra

#### Filtros
- [ ] Búsqueda por texto filtra correctamente
- [ ] Filtro por categoría funciona
- [ ] Combinación de filtros funciona
- [ ] Mensaje "No hay artículos" cuando no hay resultados

---

## 🐛 Problemas Comunes y Soluciones

### 1. "Error al cargar artículos"
**Problema:** API no responde  
**Solución:**
```bash
# Verificar que el backend esté corriendo
python manage.py runserver

# Verificar que las URLs estén correctas
http://localhost:8000/api/articulos/api/articulos/
```

### 2. "Imágenes no se cargan"
**Problema:** Rutas de archivos incorrectas  
**Solución:**
- Verificar que la carpeta `media/` existe
- Verificar configuración en `settings.py`:
  ```python
  MEDIA_URL = '/media/'
  MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
  ```
- Verificar que el servidor sirve archivos media en desarrollo

### 3. "Videos no se reproducen"
**Problema:** URL de video incorrecta  
**Solución:**
- Verificar que la URL sea de YouTube o Vimeo
- Formato correcto: `https://www.youtube.com/watch?v=VIDEO_ID`
- El código convierte automáticamente a formato embed

### 4. "Archivos no se descargan"
**Problema:** Ruta del archivo incorrecta  
**Solución:**
- Verificar que el archivo exista en `media/articulos/archivos/`
- Verificar permisos del directorio
- URL correcta: `http://localhost:8000/media/articulos/archivos/...`

### 5. "CORS Error"
**Problema:** Backend bloquea peticiones del frontend  
**Solución:**
Verificar en `settings.py`:
```python
CORS_ALLOW_ALL_ORIGINS = True  # Solo para desarrollo
```

---

## 📸 Screenshots de Referencia

### Vista esperada en Desktop:
```
┌─────────────────────────────────────────┐
│  🗞️ Artículos                           │
│  Noticias, entrevistas...              │
├─────────────────────────────────────────┤
│  🔍 [Buscar...]  📁 [Categorías ▼]     │
├─────────────────────────────────────────┤
│  Artículos Destacados                   │
│  ┌──────┐  ┌──────┐  ┌──────┐         │
│  │ IMG  │  │ IMG  │  │ IMG  │         │
│  │Title │  │Title │  │Title │         │
│  └──────┘  └──────┘  └──────┘         │
├─────────────────────────────────────────┤
│  Todos los Artículos                    │
│  ┌──────┐  ┌──────┐  ┌──────┐         │
│  │ IMG  │  │ IMG  │  │ IMG  │         │
│  │Title │  │Title │  │Title │         │
│  └──────┘  └──────┘  └──────┘         │
└─────────────────────────────────────────┘
```

### Modal de Artículo:
```
┌───────────────────────────────────────┐
│                              [X]      │
│  ┌─────────────────────────────────┐ │
│  │   [IMAGEN DESTACADA]            │ │
│  └─────────────────────────────────┘ │
│                                       │
│  📁 Categoría | 👤 Autor | 📅 Fecha  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│  # Título del Artículo                │
│                                       │
│  [Resumen destacado]                  │
│                                       │
│  Contenido completo del artículo...   │
│  Lorem ipsum dolor sit amet...        │
│                                       │
│  🎥 Video relacionado                 │
│  ┌─────────────────────────────────┐ │
│  │     [YOUTUBE EMBED]             │ │
│  └─────────────────────────────────┘ │
│                                       │
│  📎 Archivo adjunto                   │
│  → Descargar archivo                  │
└───────────────────────────────────────┘
```

---

## 🎨 Estilos Verificados

Los siguientes estilos deben coincidir con el resto del sitio:

- ✅ **Colores:** Rojo (`var(--color-red)`) para acentos
- ✅ **Tipografía:** Consistente con Home
- ✅ **Cards:** Border radius, sombras, hover effects
- ✅ **Botones:** Mismo estilo que "Ver Programación"
- ✅ **Responsive:** Grid adapta a 1, 2 o 3 columnas

---

## 📊 Datos de Prueba Sugeridos

### Artículo 1 (Destacado)
```
Título: Radio Oriente FM Celebra 14 Años al Aire
Categoría: Noticias
Resumen: Celebramos más de una década conectando a la comunidad...
Imagen: [Subir logo de la radio]
Publicado: ✅
Destacado: ✅
```

### Artículo 2 (Con Video)
```
Título: Entrevista Exclusiva con Banda Local
Categoría: Entrevistas
Video URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ
Publicado: ✅
Destacado: ❌
```

### Artículo 3 (Con Archivo)
```
Título: Programación Semanal - Marzo 2025
Categoría: Programación
Archivo: [Subir PDF con horarios]
Publicado: ✅
Destacado: ❌
```

---

## ✅ Checklist Final

Una vez probado todo:

- [ ] Backend y Frontend corriendo sin errores
- [ ] Artículos se listan correctamente
- [ ] Imágenes se cargan
- [ ] Filtros funcionan
- [ ] Modal se abre y cierra
- [ ] Videos se reproducen
- [ ] Archivos se descargan
- [ ] Diseño responsive funciona
- [ ] Consistencia visual con el resto del sitio

---

## 🎉 ¡Listo para Producción!

Si todos los checks están completos, el sistema de artículos con multimedia está listo para usar en producción.

### Próximos pasos opcionales:
1. Agregar sistema de comentarios en el frontend
2. Implementar paginación para muchos artículos
3. Agregar compartir en redes sociales
4. SEO metadata para artículos
5. Vista previa antes de publicar
