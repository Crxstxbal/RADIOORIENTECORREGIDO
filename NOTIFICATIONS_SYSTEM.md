# Sistema de Notificaciones - Radio Oriente FM

## Resumen

Se ha implementado un sistema completo de notificaciones en tiempo real para el dashboard, que permite a los administradores recibir alertas inmediatas sobre eventos importantes en la plataforma.

---

## Características Implementadas

### 1. Notificaciones Automáticas

El sistema genera notificaciones automáticamente para los siguientes eventos:

- **Mensajes de Contacto**: Cuando un usuario envía un formulario de contacto
- **Bandas Emergentes**: Cuando una banda se registra en el sistema
- **Artículos Nuevos**: Cuando otro administrador crea un artículo
- **Cambios en Programación**: Cuando se crean o modifican programas y horarios
- **Nuevas Suscripciones**: Cuando alguien se suscribe al newsletter

### 2. Interfaz de Usuario

- **Icono de campana** en el navbar del dashboard con badge de contador
- **Dropdown animado** con lista de notificaciones
- **Iconos diferenciados** por tipo de notificación (contacto, banda, artículo, etc.)
- **Estados visuales**: notificaciones no leídas con fondo destacado
- **Tiempo transcurrido** en formato legible (ej: "Hace 5 minutos")
- **Modo oscuro**: soporte completo para tema claro y oscuro

### 3. Funcionalidades

- Ver últimas 10 notificaciones en el dropdown
- Marcar notificaciones individuales como leídas al hacer clic
- Marcar todas las notificaciones como leídas con un botón
- Contador de notificaciones no leídas en tiempo real
- Actualización automática cada 30 segundos (polling)
- Enlaces directos a las secciones relacionadas (próximamente)

---

## Arquitectura Técnica

### Backend

#### Estructura de Archivos

```
backend/apps/notifications/
├── __init__.py
├── apps.py              # Configuración de la app
├── models.py            # Modelo Notification
├── serializers.py       # NotificationSerializer
├── views.py             # NotificationViewSet con API endpoints
├── signals.py           # Signals para crear notificaciones automáticas
├── urls.py              # Rutas de la API
├── admin.py             # Admin de Django
└── migrations/
    └── 0001_initial.py
```

#### Modelo Notification

[backend/apps/notifications/models.py:1-47](backend/apps/notifications/models.py#L1-L47)

**Campos principales:**
- `usuario`: Usuario que recibe la notificación (ForeignKey a User)
- `tipo`: Tipo de notificación ('contacto', 'banda', 'articulo', 'programa', 'suscripcion')
- `titulo`: Título de la notificación
- `mensaje`: Descripción detallada
- `leido`: Estado de lectura (Boolean)
- `fecha_creacion`: Timestamp automático
- `enlace`: URL opcional para navegación
- `content_type` y `object_id`: Referencia genérica al objeto origen

**Índices:**
- `(usuario, leido)` - Para consultas rápidas de no leídas
- `fecha_creacion` - Para ordenamiento

#### API Endpoints

**Base URL:** `/api/notifications/api/notificaciones/`

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Lista todas las notificaciones del usuario |
| `/no_leidas/` | GET | Solo notificaciones no leídas |
| `/contador/` | GET | Contador de notificaciones no leídas |
| `/{id}/marcar_leido/` | POST | Marcar una notificación como leída |
| `/marcar_todas_leidas/` | POST | Marcar todas como leídas |
| `/{id}/eliminar/` | DELETE | Eliminar una notificación |
| `/eliminar_leidas/` | DELETE | Eliminar todas las leídas |
| `/por_tipo/?tipo=contacto` | GET | Filtrar por tipo |

**Ejemplo de respuesta:**

```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "tipo": "contacto",
      "tipo_display": "Mensaje de Contacto",
      "titulo": "Nuevo mensaje de contacto de Juan Perez",
      "mensaje": "Juan Perez (juan@email.com) envio un mensaje de tipo 'Consulta General'",
      "leido": false,
      "fecha_creacion": "2025-11-01T10:30:00Z",
      "enlace": "/dashboard/contactos/?id=1",
      "tiempo_transcurrido": "Hace 5 minutos"
    }
  ]
}
```

#### Signals

[backend/apps/notifications/signals.py](backend/apps/notifications/signals.py)

Los signals escuchan los eventos `post_save` de los siguientes modelos:

1. **contact.Contacto** → Notifica nuevo mensaje de contacto
2. **emergente.BandaEmergente** → Notifica nueva banda registrada
3. **articulos.Articulo** → Notifica nuevo artículo (excepto al autor)
4. **radio.Programa** → Notifica creación/modificación de programa
5. **radio.HorarioPrograma** → Notifica cambios en horarios
6. **contact.Suscripcion** → Notifica nueva suscripción

**Función auxiliar:**
```python
crear_notificacion_para_staff(tipo, titulo, mensaje, enlace=None, content_type=None, object_id=None)
```
Crea notificaciones para todos los usuarios con `is_staff=True`.

### Frontend (Dashboard)

#### Componente de Notificaciones

El componente está integrado en [backend/dashboard/templates/dashboard/base.html](backend/dashboard/templates/dashboard/base.html)

**Estructura HTML:**

```html
<!-- Botón con badge -->
<button class="notification-btn" onclick="toggleNotifications()">
    <i class="fas fa-bell"></i>
    <span class="notification-badge" id="notificationBadge">0</span>
</button>

<!-- Dropdown -->
<div class="notification-dropdown" id="notificationDropdown">
    <div class="notification-header">...</div>
    <div class="notification-list" id="notificationList">...</div>
    <div class="notification-footer">...</div>
</div>
```

**Funciones JavaScript principales:**

| Función | Descripción |
|---------|-------------|
| `toggleNotifications()` | Abre/cierra el dropdown |
| `loadNotifications()` | Carga notificaciones desde la API |
| `renderNotifications(notifications)` | Renderiza la lista HTML |
| `updateBadge()` | Actualiza el contador del badge |
| `markAsRead(id)` | Marca una notificación como leída |
| `markAllAsRead()` | Marca todas como leídas |
| `getNotificationIcon(tipo)` | Retorna el ícono según el tipo |

**Polling automático:**
```javascript
// Actualiza el contador cada 30 segundos
setInterval(updateBadge, 30000);
```

---

## Uso y Flujo de Trabajo

### Escenario 1: Usuario envía formulario de contacto

1. Usuario completa formulario en frontend → POST `/api/contact/api/contactos/`
2. Django crea instancia de `Contacto`
3. Signal `notificar_nuevo_contacto` se dispara
4. Se crean notificaciones para todos los usuarios staff
5. Dashboard muestra badge con contador actualizado
6. Admin hace clic en la campana y ve la notificación
7. Admin hace clic en la notificación → se marca como leída

### Escenario 2: Banda se registra

1. Banda completa formulario → POST `/api/emergentes/api/bandas/`
2. Django crea instancia de `BandaEmergente`
3. Signal `notificar_nueva_banda` se dispara
4. Notificaciones creadas para staff
5. Badge actualizado automáticamente en el dashboard

### Escenario 3: Admin crea artículo

1. Admin A crea artículo en dashboard
2. Signal `notificar_nuevo_articulo` se dispara
3. Se crean notificaciones para todos los staff EXCEPTO Admin A
4. Admin B y Admin C ven notificación de nuevo artículo

---

## Estilos y Diseño

### Colores por Tipo de Notificación

| Tipo | Color | Ícono |
|------|-------|-------|
| Contacto | Azul (#3b82f6) | Sobre (fa-envelope) |
| Banda | Verde (#10b981) | Música (fa-music) |
| Artículo | Naranja (#f59e0b) | Periódico (fa-newspaper) |
| Programa | Morado (#8b5cf6) | Micrófono (fa-microphone) |
| Suscripción | Rosa (#ec4899) | Usuario+ (fa-user-plus) |

### Responsive Design

- **Desktop**: Dropdown de 380px de ancho
- **Mobile**: Dropdown ocupa casi todo el ancho (100vw - 2rem)
- Badge siempre visible en ambos tamaños

---

## Configuración

### Variables de Entorno

No requiere configuración adicional. Usa las credenciales de base de datos existentes.

### Permisos

- **Staff**: Puede ver y gestionar sus notificaciones
- **Usuarios normales**: No tienen acceso al sistema de notificaciones (solo para dashboard)

---

## Próximas Mejoras

### Corto Plazo

- [ ] Enlaces funcionales a las secciones específicas (contactos, bandas, etc.)
- [ ] Página dedicada para ver todas las notificaciones históricas
- [ ] Filtros por tipo de notificación
- [ ] Búsqueda en notificaciones

### Medio Plazo

- [ ] **WebSockets**: Notificaciones en tiempo real sin polling
- [ ] Notificaciones push del navegador (Web Push API)
- [ ] Personalización: permitir al usuario elegir qué tipos recibir
- [ ] Notificaciones por email opcionales

### Largo Plazo

- [ ] Sistema de prioridades (alta, media, baja)
- [ ] Notificaciones agrupadas (ej: "5 bandas nuevas hoy")
- [ ] Estadísticas de notificaciones
- [ ] Integración con Slack/Discord para administradores

---

## Troubleshooting

### Problema: No aparecen notificaciones

**Solución:**
1. Verificar que el usuario tenga `is_staff=True`
2. Abrir DevTools → Console y verificar errores de red
3. Verificar que la API responda: `GET /api/notifications/api/notificaciones/`

### Problema: Badge no se actualiza

**Solución:**
1. Verificar que el polling esté activo (cada 30 segundos)
2. Verificar endpoint: `GET /api/notifications/api/notificaciones/contador/`
3. Revisar console para errores de fetch

### Problema: Error 500 al marcar como leída

**Solución:**
1. Verificar que el token CSRF esté presente
2. Revisar logs del backend: `python manage.py runserver`
3. Verificar permisos del usuario

---

## Testing

### Crear notificación de prueba

Desde el shell de Django:

```python
python manage.py shell

from apps.notifications.models import Notification
from apps.users.models import User

# Crear notificación de prueba
admin_user = User.objects.filter(is_staff=True).first()

Notification.objects.create(
    usuario=admin_user,
    tipo='contacto',
    titulo='Notificacion de prueba',
    mensaje='Este es un mensaje de prueba del sistema',
    enlace='/dashboard/'
)
```

### Probar signals

```python
from apps.contact.models import Contacto, TipoAsunto

# Esto debe generar notificación automáticamente
tipo = TipoAsunto.objects.first()
Contacto.objects.create(
    nombre='Test User',
    email='test@test.com',
    tipo_asunto=tipo,
    mensaje='Mensaje de prueba'
)

# Verificar que se crearon notificaciones
from apps.notifications.models import Notification
print(Notification.objects.count())
```

---

## Seguridad

### Medidas Implementadas

1. **Autenticación requerida**: Solo usuarios autenticados pueden acceder
2. **Filtrado por usuario**: Cada usuario solo ve sus propias notificaciones
3. **Solo staff**: Solo usuarios con `is_staff=True` reciben notificaciones
4. **CSRF protection**: Todas las mutaciones requieren token CSRF
5. **Permisos**: ViewSet usa `IsAuthenticated` permission

### Recomendaciones

- Limitar tasa de requests para evitar spam
- Implementar limpieza automática de notificaciones antiguas (> 90 días)
- Considerar rate limiting en el polling

---

## API Reference

### Paginación

Todos los endpoints de lista soportan paginación:

```
GET /api/notifications/api/notificaciones/?page=2&page_size=20
```

### Filtrado

```
GET /api/notifications/api/notificaciones/?tipo=contacto
GET /api/notifications/api/notificaciones/no_leidas/
```

### Ordenamiento

Por defecto, ordenadas por `-fecha_creacion` (más reciente primero).

---

## Archivos Modificados

### Nuevos Archivos

- `backend/apps/notifications/` (app completa)
- `NOTIFICATIONS_SYSTEM.md` (esta documentación)

### Archivos Modificados

- [backend/radio_oriente/settings.py](backend/radio_oriente/settings.py#L41) - Agregada app en INSTALLED_APPS
- [backend/radio_oriente/urls.py](backend/radio_oriente/urls.py#L45) - Agregada ruta de API
- [backend/dashboard/templates/dashboard/base.html](backend/dashboard/templates/dashboard/base.html) - Integrado componente UI

---

## Migraciones

```bash
# Ya ejecutadas
python manage.py makemigrations notifications
python manage.py migrate notifications
```

---

## Monitoreo

### Consultas útiles

```python
# Notificaciones no leídas por usuario
from apps.notifications.models import Notification
from apps.users.models import User

for user in User.objects.filter(is_staff=True):
    count = Notification.objects.filter(usuario=user, leido=False).count()
    print(f"{user.email}: {count} no leídas")

# Notificaciones creadas hoy
from django.utils import timezone
from datetime import timedelta

hoy = timezone.now().date()
count = Notification.objects.filter(fecha_creacion__date=hoy).count()
print(f"Notificaciones hoy: {count}")

# Notificaciones por tipo
from django.db.models import Count
Notification.objects.values('tipo').annotate(total=Count('id'))
```

---

## Créditos

**Desarrollado por:** Claude Code
**Fecha:** 2025-11-01
**Versión:** 1.0
**Proyecto:** Radio Oriente FM - Sistema de Gestión

---

## Changelog

### v1.0 (2025-11-01)
- ✅ Implementación inicial del sistema de notificaciones
- ✅ Signals para 5 tipos de eventos
- ✅ API RESTful completa
- ✅ Componente UI en dashboard con polling
- ✅ Soporte para tema oscuro
- ✅ Responsive design
- ✅ Documentación completa

### Próxima versión (v1.1)
- WebSockets para notificaciones en tiempo real
- Enlaces funcionales a secciones específicas
- Notificaciones push del navegador
