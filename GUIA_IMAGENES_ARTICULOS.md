# 📸 Guía de Imágenes para Artículos

## 🎯 Resumen

Ahora los artículos soportan **DOS tipos de imágenes**:

1. **📸 Imagen Portada (Banner)** - Horizontal para el modal
2. **🖼️ Imagen Thumbnail** - Cuadrada para las tarjetas de lista y modal

---

## 🖼️ Tipos de Imágenes

### 1. Imagen Portada (Banner)
- **Resolución recomendada:** 1200 x 400 px (horizontal)
- **Uso:** Se muestra en la parte superior del modal cuando abres el artículo completo
- **Formato:** JPG, PNG, WebP
- **Peso máximo:** 2 MB

### 2. Imagen Thumbnail (Miniatura Cuadrada)
- **Resolución recomendada:** 600 x 600 px (cuadrada)
- **Uso:** 
  - En las tarjetas de la lista de artículos
  - Dentro del modal, al lado izquierdo del contenido
- **Formato:** JPG, PNG, WebP
- **Peso máximo:** 1 MB

---

## 📋 Cómo Agregar Imágenes desde el Admin

### Paso 1: Entrar al Admin de Django

```
http://localhost:8000/admin/articulos/articulo/
```

### Paso 2: Crear o Editar un Artículo

1. Haz clic en **"Añadir artículo"** o edita uno existente
2. Llena la información básica (título, autor, categoría, contenido)

### Paso 3: Subir las Imágenes

En la sección **"Multimedia - Imágenes"** verás:

```
┌─────────────────────────────────────────────────┐
│ Multimedia - Imágenes                           │
├─────────────────────────────────────────────────┤
│ 📸 Imagen Portada (Banner):                     │
│ Horizontal 1200x400px para el modal            │
│                                                  │
│ 🖼️ Imagen Thumbnail:                            │
│ Cuadrada 600x600px para las tarjetas           │
└─────────────────────────────────────────────────┘
```

**Campos:**
- **Imagen Banner (Horizontal):** Sube tu imagen horizontal
  - ✅ **Vista previa en vivo** aparece al lado
  
- **Imagen Miniatura (Cuadrada):** Sube tu imagen cuadrada
  - ✅ **Vista previa en vivo** aparece al lado

- **URL de imagen externa:** (Opcional) Si prefieres usar una URL externa

### Paso 4: Publicar

1. Marca como **"Publicado"** ✅
2. Opcionalmente marca como **"Destacado"** para que aparezca en la sección destacada
3. Guarda el artículo

---

## 🎨 Cómo se Muestran las Imágenes

### En la Lista de Artículos:
```
┌────────────────┐
│  [THUMBNAIL]   │  ← Imagen cuadrada 
│   (600x600)    │
├────────────────┤
│ Título         │
│ Descripción... │
│ [Leer más]     │
└────────────────┘
```

### En el Modal del Artículo:
```
┌──────────────────────────────────────────┐
│        [BANNER HORIZONTAL]               │ ← Imagen horizontal
│           (1200x400)                     │
├──────────────────────────────────────────┤
│                                          │
│  ┌────────┐  Título del Artículo       │
│  │ THUMB  │                             │
│  │(600x600│  Contenido del artículo...  │ ← Thumbnail al lado
│  │   )    │  Lorem ipsum dolor sit amet │
│  └────────┘  consectetur adipiscing...  │
│                                          │
│              [Video si existe]           │
│              [Archivo adjunto]           │
└──────────────────────────────────────────┘
```

---

## ✅ Mejoras del Admin

### Vista de Lista:
- Ahora ves **miniaturas pequeñas** de las imágenes en la columna "Imágenes" 📷
- Puedes identificar rápidamente qué artículos tienen imágenes

### Vista de Edición:
- **Previsualizaciones en vivo** al lado de cada campo de imagen
- **Descripciones claras** de qué resolución usar
- Layout organizado en secciones colapsables

---

## 💡 Consejos

### 1. Optimiza tus Imágenes
Usa herramientas como:
- [TinyPNG](https://tinypng.com/) - Comprimir sin perder calidad
- [Squoosh](https://squoosh.app/) - Optimizador de Google
- Photoshop, GIMP, etc.

### 2. Dimensiones Exactas
```bash
# Imagen Banner
1200 x 400 px (ratio 3:1)

# Imagen Thumbnail  
600 x 600 px (ratio 1:1)
```

### 3. ¿Qué pasa si solo subo una imagen?
- Si subes **solo Banner**: Se usará en modal y también como thumbnail (recortada)
- Si subes **solo Thumbnail**: Se usará en tarjetas y modal
- Si subes **ambas**: Cada una se usa en su lugar óptimo ✅ (recomendado)

### 4. Prioridad de Imágenes
El sistema usa este orden:
```python
# Para tarjetas (lista):
1. imagen_thumbnail  ← Primero busca thumbnail
2. imagen_url        ← Si no hay, usa URL externa
3. imagen_portada    ← Si no hay, usa la portada

# Para modal (banner):
1. imagen_portada    ← Primero busca portada
2. imagen_url        ← Si no hay, usa URL externa
```

---

## 🔧 Solución de Problemas

### ❌ "La imagen no aparece"
1. Verifica que el artículo esté **"Publicado"**
2. Refresca la página con Ctrl+F5
3. Verifica que la imagen se subió correctamente en el admin

### ❌ "La imagen se ve pixelada"
- Sube una imagen con las dimensiones recomendadas
- La resolución mínima es importante para que se vea bien

### ❌ "El thumbnail se ve estirado"
- Asegúrate de usar una imagen **cuadrada** (600x600)
- El sistema automáticamente aplica `object-fit: cover` para mantener proporciones

---

## 📁 Ubicación de las Imágenes

Las imágenes se guardan en:
```
MEDIA_ROOT/articulos/imagenes/YYYY/MM/slug-del-articulo.jpg
```

Por ejemplo:
```
media/
  articulos/
    imagenes/
      2025/
        10/
          la-decadencia-de-call-of-duty.jpg        ← Banner
          la-decadencia-de-call-of-duty-thumb.jpg  ← Thumbnail
```

---

## 🎉 Resultado Final

Con estas mejoras, tus artículos ahora se ven **profesionales** con:
- ✅ Imágenes optimizadas para cada contexto
- ✅ Layout responsivo (se adapta a móvil y desktop)
- ✅ Carga rápida con imágenes del tamaño correcto
- ✅ Interfaz intuitiva en el admin

¡Disfruta creando contenido visual atractivo para Radio Oriente FM! 🎙️📰
