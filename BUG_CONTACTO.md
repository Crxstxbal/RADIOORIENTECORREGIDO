# Bug en Página de Contacto - Análisis y Solución

## Problema
La página de Contacto muestra contenido por un segundo y luego se pone en blanco.

## Causa Raíz
El archivo `frontend/src/pages/Contacto.js` está usando `axios` directamente en lugar de `fetch` nativo.

El interceptor de axios en `frontend/src/utils/api.js` (líneas 33-36) redirige automáticamente a `/login` cuando recibe un error 401:

```javascript
if (error.response?.status === 401) {
  localStorage.removeItem('token');
  window.location.href = '/login';  // <-- Esto causa la pantalla en blanco
}
```

Cuando un usuario NO autenticado visita `/contacto`, y algún endpoint responde con 401, el interceptor hace redirect, causando la pantalla en blanco.

## Solución

Cambiar `axios` por `fetch` nativo en Contact.js para evitar el interceptor:

### Cambios necesarios en `frontend/src/pages/Contacto.js`:

**1. Remover import de axios (línea 3):**
```javascript
// ANTES:
import axios from 'axios';

// DESPUÉS:
// (remover esta línea completamente)
```

**2. Cambiar el useEffect (líneas 20-45):**
```javascript
// ANTES:
const tiposResponse = await axios.get('/api/contact/api/tipos-asunto/');
setTiposAsunto(tiposResponse.data);

// DESPUÉS:
const tiposResponse = await fetch('/api/contact/api/tipos-asunto/', {
  method: 'GET',
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  }
});

if (tiposResponse.ok) {
  const tiposData = await tiposResponse.json();
  setTiposAsunto(tiposData.results || tiposData);
}
```

**3. Cambiar handleSubmit (líneas 54-77):**
```javascript
// ANTES:
const token = localStorage.getItem('token');
const headers = token ? { Authorization: `Token ${token}` } : {};

await axios.post('/api/contact/api/contactos/', formData, { headers });

// DESPUÉS:
const token = localStorage.getItem('token');
const headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
};

if (token) {
  headers['Authorization'] = `Token ${token}`;
}

const response = await fetch('/api/contact/api/contactos/', {
  method: 'POST',
  headers: headers,
  body: JSON.stringify(formData)
});

if (response.ok) {
  toast.success('Mensaje enviado exitosamente...');
  // ... reset form
} else {
  toast.error('Error al enviar el mensaje...');
}
```

## Archivos Afectados
- `frontend/src/pages/Contacto.js` - Necesita modificación
- `frontend/src/pages/Contacto.js.bak` - Backup creado

## Instrucciones Manuales

1. Abrir `frontend/src/pages/Contacto.js`
2. Remover línea 3: `import axios from 'axios';`
3. Reemplazar todas las llamadas `axios.get()` y `axios.post()` con `fetch()`
4. Usar el código de ejemplo de arriba

O restaurar desde backup y aplicar cambios:
```bash
cd frontend/src/pages
cp Contacto.js.bak Contacto.js
# Luego aplicar cambios manualmente
```

