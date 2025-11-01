# Guía de Seguridad - Radio Oriente FM

## Configuración Inicial de Seguridad

### 1. Variables de Entorno

**IMPORTANTE:** Antes de ejecutar el proyecto, debes configurar correctamente las variables de entorno.

#### Backend

1. Copia el archivo de ejemplo:
   ```bash
   cd backend
   cp .env.example .env
   ```

2. Genera una SECRET_KEY segura:
   ```bash
   python generate_secret_key.py
   ```

3. Copia la SECRET_KEY generada y pégala en tu archivo `.env`

4. Configura las demás variables según tu entorno:
   - `DEBUG=False` en producción (actualmente `True` para desarrollo)
   - `ALLOWED_ORIGINS` - Lista de dominios permitidos para CORS
   - `DATABASE_URL` - URL de tu base de datos PostgreSQL (Supabase)
   - `EMAIL_HOST_USER` y `EMAIL_HOST_PASSWORD` - Credenciales de email

#### Frontend

1. Copia el archivo de ejemplo:
   ```bash
   cd frontend
   cp .env.example .env
   ```

2. Configura las URLs según tu entorno:
   - `VITE_API_URL` - URL del backend API
   - `VITE_DASHBOARD_URL` - URL del dashboard de administración

### 2. Configuración de Producción

Cuando despliegues a producción, asegúrate de:

#### Backend (`backend/.env`)

```env
# OBLIGATORIO: Cambiar estos valores
DEBUG=False
CORS_ALLOW_ALL_ORIGINS=False
SECRET_KEY=[tu-clave-generada-con-generate_secret_key.py]

# Configurar dominios específicos
ALLOWED_ORIGINS=https://tudominio.com,https://www.tudominio.com
ALLOWED_HOSTS=tudominio.com,www.tudominio.com

# Base de datos de producción
USE_SQLITE=False
DATABASE_URL=postgresql://[usuario]:[contraseña]@[host]:[puerto]/[database]

# Email de producción
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password

# URLs de producción
FRONTEND_URL=https://tudominio.com
DASHBOARD_URL=https://tudominio.com/dashboard/
```

#### Frontend (`frontend/.env`)

```env
VITE_API_URL=https://api.tudominio.com
VITE_DASHBOARD_URL=https://tudominio.com/dashboard/
```

### 3. Configuraciones de Seguridad Adicionales

#### Django Settings

El archivo `backend/radio_oriente/settings.py` ya incluye configuraciones de seguridad como:

- Validación de contraseñas
- CORS configurado dinámicamente desde variables de entorno
- SSL requerido para conexiones a base de datos en producción
- Autenticación basada en tokens

#### Recomendaciones Adicionales para Producción

1. **HTTPS**: Siempre usa HTTPS en producción
   - Configura SSL/TLS en tu servidor
   - Redirige todo el tráfico HTTP a HTTPS

2. **Headers de Seguridad**: Agrega estos settings en producción:
   ```python
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   SECURE_BROWSER_XSS_FILTER = True
   SECURE_CONTENT_TYPE_NOSNIFF = True
   X_FRAME_OPTIONS = 'DENY'
   ```

3. **Archivos Estáticos**: Configura un servidor web (Nginx/Apache) para servir archivos estáticos

4. **Base de Datos**:
   - Usa contraseñas fuertes
   - Configura Row Level Security (RLS) en Supabase
   - Realiza backups regulares

5. **Monitoring**:
   - Configura logging apropiado
   - Monitorea intentos de acceso fallidos
   - Usa servicios como Sentry para rastrear errores

### 4. Credenciales y Secretos

**NUNCA** hagas commit de:

- Archivos `.env`
- Contraseñas
- API keys
- SECRET_KEY de Django
- Credenciales de base de datos
- Tokens de autenticación

El archivo `.gitignore` ya está configurado para prevenir esto, pero siempre verifica antes de hacer commit.

### 5. Historial de Git

Si accidentalmente hiciste commit de credenciales:

1. Cambia TODAS las credenciales inmediatamente
2. Remueve el archivo del historial de git:
   ```bash
   git rm --cached ruta/al/archivo
   git commit -m "Remove sensitive file from tracking"
   ```
3. Considera usar `git filter-branch` o `BFG Repo-Cleaner` para limpiar el historial completamente

### 6. Contacto de Seguridad

Si encuentras alguna vulnerabilidad de seguridad, por favor contacta al equipo de desarrollo:

- Leonardo Montenegro
- Cristóbal Castro
- Joaquín Molina

---

**Última actualización:** 2025-11-01
