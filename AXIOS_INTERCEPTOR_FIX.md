# Solucion: Problema de Pantalla en Blanco en Contacto y Emergentes

## Fecha: 2025-11-01

## Problemas Identificados

### 1. Pagina de Contacto - Error al enviar formulario

**Sintoma:**
- El formulario mostraba el error: "Error al enviar el mensaje. Intentalo de nuevo."
- La pagina se mostraba brevemente y luego se iba en blanco
- No habia errores en la terminal del backend

**Causa raiz:**
- Faltaba el import de `axios` en [frontend/src/pages/Contacto.js](frontend/src/pages/Contacto.js)
- El componente intentaba usar `axios.get()` y `axios.post()` sin importarlo
- Esto causaba un error de JavaScript que hacia que React mostrara pantalla en blanco

### 2. Pagina de Bandas Emergentes - Pantalla en blanco

**Sintoma:**
- La pagina se mostraba un segundo y luego se iba en blanco
- Similar al problema de Contacto

**Causa raiz:**
- El interceptor global de axios redirigía a `/login` cuando cualquier peticion retornaba 401
- Esto incluia peticiones publicas (sin autenticacion) que fallan por otras razones
- Como la pagina de emergentes hace multiples peticiones al cargar (paises, ciudades, generos), si alguna fallaba con 401, se redirigía automaticamente
- La redireccion causaba que la pagina se viera en blanco momentaneamente

## Soluciones Implementadas

### Solucion 1: Agregar import de axios en Contacto.js

**Archivo modificado:** [frontend/src/pages/Contacto.js](frontend/src/pages/Contacto.js#L3)

```javascript
// ANTES
import React, { useState, useEffect } from 'react';
import { Mail, Phone, MapPin, Send } from 'lucide-react';

import toast from 'react-hot-toast';

// DESPUES
import React, { useState, useEffect } from 'react';
import { Mail, Phone, MapPin, Send } from 'lucide-react';
import axios from 'axios';  // <-- AGREGADO
import toast from 'react-hot-toast';
```

### Solucion 2: Mejorar interceptor global de axios

**Archivo modificado:** [frontend/src/utils/api.js](frontend/src/utils/api.js#L3-L26)

**Cambios:**

1. **Interceptor global de axios agregado** para manejar errores 401 de forma inteligente:

```javascript
// Configurar interceptor global de axios para todas las instancias
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    // Solo redirigir a login si hay un token valido que expiro
    // No redirigir para peticiones publicas sin token
    if (error.response?.status === 401) {
      const hasToken = localStorage.getItem('token');

      // Solo redirigir si habia un token (sesion expirada)
      if (hasToken) {
        localStorage.removeItem('token');
        // Evitar redireccion si ya estamos en /login o /emergente o /contacto
        const currentPath = window.location.pathname;
        if (currentPath !== '/login' && currentPath !== '/emergente' && currentPath !== '/contacto') {
          window.location.href = '/login';
        }
      }
      // Si no hay token, es una peticion publica que fallo - no redirigir
    }

    return Promise.reject(error);
  }
);
```

**Logica implementada:**

- ✅ **Con token + 401**: Token expiro → Redirigir a `/login`
- ✅ **Sin token + 401**: Peticion publica que fallo → NO redirigir
- ✅ **Ya en rutas publicas**: `/contacto`, `/emergente`, `/login` → NO redirigir

2. **Simplificacion del interceptor de instancia api**:

Removimos la logica de redireccion del interceptor de la instancia `api` ya que ahora se maneja globalmente.

### Solucion 3: Importar api.js en index.js

**Archivo modificado:** [frontend/src/index.js](frontend/src/index.js#L7)

```javascript
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { AuthProvider } from './contexts/AuthContext';
import './utils/api'; // Configurar interceptores de axios globalmente  <-- AGREGADO
```

**Por que es necesario:**

- Al importar `api.js` tempranamente, el interceptor global se configura antes de que cualquier componente intente usar axios
- Esto asegura que TODAS las instancias de axios (importadas con `import axios from 'axios'`) tengan el interceptor configurado

## Flujo de Autenticacion Mejorado

### Caso 1: Usuario NO autenticado accede a /contacto

```
1. Usuario abre /contacto
2. Componente intenta cargar tipos de asunto: GET /api/contact/api/tipos-asunto/
3. Backend responde con datos (AllowAny permission)
4. Componente se renderiza correctamente
5. Usuario llena formulario
6. Submit: POST /api/contact/api/contactos/
7. Backend crea contacto (AllowAny permission)
8. Exito! Notificacion mostrada
```

### Caso 2: Usuario NO autenticado accede a /emergente

```
1. Usuario abre /emergente
2. Componente intenta cargar:
   - GET /api/ubicacion/paises/
   - GET /api/radio/api/generos/
3. Si alguno retorna 401 (por cualquier razon):
   - hasToken = false
   - NO se redirige a /login
   - Error se maneja en el catch del componente
   - Componente muestra fallback o continua con datos por defecto
4. Usuario llena formulario
5. Submit funciona correctamente
```

### Caso 3: Usuario autenticado con token expirado

```
1. Usuario autenticado (token en localStorage)
2. Intenta acceder a cualquier recurso protegido
3. Backend responde 401 (token invalido/expirado)
4. Interceptor detecta:
   - hasToken = true
   - currentPath !== '/login'
5. Redirige a /login
6. Token removido de localStorage
```

## Archivos Modificados

### Backend
Ningun cambio necesario en backend.

### Frontend

1. **[frontend/src/pages/Contacto.js](frontend/src/pages/Contacto.js)**
   - Linea 3: Agregado `import axios from 'axios';`

2. **[frontend/src/utils/api.js](frontend/src/utils/api.js)**
   - Lineas 3-26: Agregado interceptor global de axios
   - Lineas 51-64: Simplificado interceptor de instancia api

3. **[frontend/src/index.js](frontend/src/index.js)**
   - Linea 7: Agregado `import './utils/api';`

## Testing

### Test 1: Formulario de Contacto

```bash
1. Abrir http://localhost:3000/contacto (sin autenticacion)
2. Llenar formulario:
   - Nombre: Test User
   - Email: test@test.com
   - Telefono: +56912345678
   - Tipo de Asunto: Seleccionar uno
   - Mensaje: "Mensaje de prueba"
3. Click en "Enviar Mensaje"
4. Verificar: "Mensaje enviado exitosamente"
5. Verificar en dashboard: Notificacion de nuevo contacto
```

### Test 2: Formulario de Bandas Emergentes

```bash
1. Abrir http://localhost:3000/emergente (sin autenticacion)
2. Verificar que la pagina se carga correctamente
3. Verificar que los selects de pais/ciudad/comuna se llenan
4. Llenar formulario completo
5. Submit
6. Verificar exito
7. Verificar notificacion en dashboard
```

### Test 3: Token Expirado

```bash
1. Login en la aplicacion
2. En DevTools Console: localStorage.setItem('token', 'token_invalido')
3. Intentar acceder a /dashboard
4. Verificar redireccion a /login
5. Verificar token removido de localStorage
```

## Problemas Prevenidos

### ✅ Antes de la solucion:

- ❌ Pantalla en blanco en /contacto
- ❌ Pantalla en blanco en /emergente
- ❌ Redireccion innecesaria a /login en paginas publicas
- ❌ Bucles de redireccion

### ✅ Despues de la solucion:

- ✅ Paginas publicas funcionan correctamente
- ✅ Formularios publicos se pueden enviar sin autenticacion
- ✅ Sesiones expiradas se manejan correctamente
- ✅ No hay redirecciones innecesarias

## Mejores Practicas Aplicadas

1. **Interceptor global inteligente**: Solo redirige cuando realmente es necesario
2. **Verificacion de token**: Diferencia entre "sin token" y "token expirado"
3. **Proteccion de rutas**: Evita redirecciones en paginas publicas
4. **Imports centralizados**: api.js se importa una vez al inicio
5. **Manejo de errores**: Cada componente maneja sus propios errores de forma graceful

## Notas Adicionales

### Endpoints publicos (AllowAny)

Los siguientes endpoints NO requieren autenticacion:

```python
# Contacto
POST   /api/contact/api/contactos/              # Crear mensaje
GET    /api/contact/api/tipos-asunto/           # Listar tipos

# Bandas Emergentes
POST   /api/emergentes/api/bandas/              # Registrar banda
GET    /api/radio/api/generos/                  # Listar generos

# Ubicacion
GET    /api/ubicacion/paises/                   # Listar paises
GET    /api/ubicacion/ciudades/por_pais/        # Listar ciudades
GET    /api/ubicacion/comunas/por_ciudad/       # Listar comunas
```

### Endpoints protegidos (IsAuthenticated)

```python
# Dashboard
GET    /dashboard/*                             # Requiere staff
GET    /api/notifications/api/notificaciones/  # Requiere autenticacion
```

## Troubleshooting

### Problema: Todavia se ve pantalla en blanco

**Solucion:**
1. Limpiar cache del navegador (Ctrl + Shift + Delete)
2. Hard refresh (Ctrl + F5)
3. Verificar DevTools → Console para errores
4. Verificar DevTools → Network para ver peticiones fallidas

### Problema: Formulario no envia

**Solucion:**
1. Verificar DevTools → Network → POST request
2. Ver Response del backend
3. Verificar que todos los campos requeridos esten llenos
4. Verificar que el tipo_asunto sea un ID valido

### Problema: Sigue redirigiendo a /login

**Solucion:**
1. Abrir DevTools → Application → Local Storage
2. Borrar el token manualmente
3. Hacer hard refresh
4. Intentar de nuevo

---

**Desarrollado por:** Claude Code
**Fecha:** 2025-11-01
**Version:** 1.0
**Proyecto:** Radio Oriente FM
