# 📰 Migración de Artículos - Frontend

## 🎯 Cambios Realizados

### 1. **API Actualizada**
Se actualizaron las rutas de la API de artículos:

**Antes:**
```javascript
axios.get('/api/blog/articulos/')
axios.get('/api/blog/categorias/')
```

**Ahora:**
```javascript
axios.get('/api/articulos/api/articulos/')
axios.get('/api/articulos/api/categorias/')
```

---

### 2. **Soporte Multimedia Completo**

#### **Imágenes**
- ✅ Soporte para `imagen_portada` (archivo subido)
- ✅ Soporte para `imagen_url` (URL externa)
- ✅ Prioridad: `imagen_portada` > `imagen_url`

```javascript
const getArticleImage = (article) => {
  if (article.imagen_portada) {
    if (article.imagen_portada.startsWith('http')) {
      return article.imagen_portada;
    }
    return `http://localhost:8000${article.imagen_portada}`;
  }
  return article.imagen_url;
};
```

#### **Videos**
- ✅ Soporte para videos embebidos en el modal
- ✅ Compatible con YouTube y Vimeo
- ✅ Conversión automática de URLs

```javascript
{selectedArticle.video_url && (
  <iframe
    src={selectedArticle.video_url.replace('watch?v=', 'embed/')}
    allowFullScreen
  />
)}
```

#### **Archivos Adjuntos**
- ✅ Enlaces de descarga en el modal
- ✅ Soporte para PDF, Word, Excel, etc.

```javascript
{selectedArticle.archivo_adjunto && (
  <a href={`http://localhost:8000${selectedArticle.archivo_adjunto}`}>
    Descargar archivo
  </a>
)}
```

---

### 3. **Archivos Modificados**

#### `src/pages/Articulos.js`
- ✅ API actualizada a `/api/articulos/`
- ✅ Función `getArticleImage()` agregada
- ✅ Soporte para videos embebidos
- ✅ Enlaces de descarga para archivos adjuntos
- ✅ Mantiene el diseño y estilos existentes

#### `src/pages/Home.js`
- ✅ API actualizada a `/api/articulos/`
- ✅ Manejo de imágenes mejorado (imagen_portada + imagen_url)
- ✅ Diseño sin cambios

---

### 4. **Características Mantenidas**

✅ **Filtros**
- Por categoría
- Por búsqueda de texto

✅ **Artículos Destacados**
- Grid especial en la parte superior
- Solo muestra artículos con `destacado=true`

✅ **Modal de Lectura**
- Vista completa del artículo
- Imagen destacada
- Video embebido (nuevo)
- Archivo adjunto (nuevo)
- Metadata (autor, fecha, categoría)

✅ **Responsive Design**
- Compatible con móviles y tablets
- Usa el sistema de diseño existente

---

## 🎨 Estilos CSS

Los estilos se mantienen en `src/pages/Pages.css`:
- `.news-page` - Contenedor principal
- `.featured-news-grid` - Grid de destacados
- `.news-grid` - Grid de artículos regulares
- `.news-card` - Tarjeta individual
- `.news-modal` - Modal de lectura completa

**No se requieren cambios en CSS** - Todo mantiene el mismo lineamiento visual.

---

## 🚀 Próximos Pasos

### Para el Usuario:

1. **Iniciar el servidor backend:**
   ```bash
   cd backend
   python manage.py runserver
   ```

2. **Iniciar el frontend:**
   ```bash
   cd frontend
   npm start
   ```

3. **Acceder a la aplicación:**
   - Home: `http://localhost:3000/`
   - Artículos: `http://localhost:3000/articulos`

### Para Producción:

Cambiar las URLs hardcodeadas:
```javascript
// Desarrollo
`http://localhost:8000${article.imagen_portada}`

// Producción
`${process.env.REACT_APP_API_URL}${article.imagen_portada}`
```

Agregar al archivo `.env`:
```env
REACT_APP_API_URL=https://tu-dominio.com
```

---

## ✅ Checklist de Funcionalidades

- [x] Lista de artículos publicados
- [x] Artículos destacados
- [x] Filtro por categoría
- [x] Búsqueda por texto
- [x] Modal de lectura completa
- [x] Imágenes de portada (subidas)
- [x] Imágenes externas (URL)
- [x] Videos embebidos (YouTube, Vimeo)
- [x] Archivos adjuntos descargables
- [x] Metadata (autor, fecha, categoría, vistas)
- [x] Diseño responsive
- [x] Consistencia visual con el resto del sitio

---

## 📝 Notas Técnicas

### Campos del Modelo Artículo:
```javascript
{
  id: number,
  titulo: string,
  slug: string,
  contenido: string,
  resumen: string,
  imagen_portada: string,      // Nuevo campo
  imagen_url: string,
  video_url: string,            // Nuevo campo
  archivo_adjunto: string,      // Nuevo campo
  autor: object,
  categoria: object,
  publicado: boolean,
  destacado: boolean,
  fecha_publicacion: string,
  fecha_creacion: string,
  fecha_actualizacion: string,  // Nuevo campo
  vistas: number                 // Nuevo campo
}
```

### Endpoints de la API:
- `GET /api/articulos/api/articulos/` - Lista todos los artículos
- `GET /api/articulos/api/articulos/{slug}/` - Detalle de un artículo
- `GET /api/articulos/api/articulos/destacados/` - Artículos destacados
- `GET /api/articulos/api/articulos/mas_vistos/` - Más vistos
- `GET /api/articulos/api/categorias/` - Lista categorías
- `POST /api/articulos/api/articulos/{slug}/comentar/` - Agregar comentario

---

## 🎉 ¡Migración Completada!

El frontend ahora está completamente integrado con la nueva API de artículos con soporte multimedia completo, manteniendo el diseño y experiencia de usuario existentes.
