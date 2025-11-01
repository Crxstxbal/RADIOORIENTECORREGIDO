# Actualización de Paginación en Dashboard

## Estado Actual

**✅ YA IMPLEMENTADO:**
- Bandas Emergentes: 20 items por página (línea 823)

**❌ FALTA IMPLEMENTAR:**
- Usuarios
- Artículos
- Contactos

## Cambios a Realizar

### 1. Vista de Usuarios (línea 67-70)

**ANTES:**
```python
@login_required
@user_passes_test(is_staff_user)
def dashboard_users(request):
    """Gestión de usuarios"""
    users = User.objects.all().order_by('-fecha_creacion')
    return render(request, 'dashboard/users.html', {'users': users})
```

**DESPUÉS:**
```python
@login_required
@user_passes_test(is_staff_user)
def dashboard_users(request):
    """Gestión de usuarios"""
    users_list = User.objects.all().order_by('-fecha_creacion')

    # Paginación
    paginator = Paginator(users_list, 25)  # 25 usuarios por página
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)

    return render(request, 'dashboard/users.html', {
        'users': users,
        'total_users': paginator.count
    })
```

### 2. Vista de Artículos (línea 74-90)

**ANTES:**
```python
@login_required
@user_passes_test(is_staff_user)
def dashboard_articulos(request):
    """Gestión de artículos"""
    articulos = Articulo.objects.select_related('autor', 'categoria').all().order_by('-fecha_creacion')
    categorias = Categoria.objects.all().order_by('nombre')

    # Contadores para tarjetas: total, publicados y borradores
    total_articles = articulos.count()
    published_count = Articulo.objects.filter(publicado=True).count()
    draft_count = Articulo.objects.filter(publicado=False).count()

    return render(request, 'dashboard/articulos.html', {
        'articulos': articulos,
        'categorias': categorias,
        'total_articles': total_articles,
        'published_count': published_count,
        'draft_count': draft_count,
    })
```

**DESPUÉS:**
```python
@login_required
@user_passes_test(is_staff_user)
def dashboard_articulos(request):
    """Gestión de artículos"""
    articulos_list = Articulo.objects.select_related('autor', 'categoria').all().order_by('-fecha_creacion')
    categorias = Categoria.objects.all().order_by('nombre')

    # Contadores para tarjetas: total, publicados y borradores
    total_articles = Articulo.objects.count()
    published_count = Articulo.objects.filter(publicado=True).count()
    draft_count = Articulo.objects.filter(publicado=False).count()

    # Paginación
    paginator = Paginator(articulos_list, 25)  # 25 artículos por página
    page_number = request.GET.get('page')
    articulos = paginator.get_page(page_number)

    return render(request, 'dashboard/articulos.html', {
        'articulos': articulos,
        'categorias': categorias,
        'total_articles': total_articles,
        'published_count': published_count,
        'draft_count': draft_count,
    })
```

### 3. Vista de Contactos (línea 985-1041)

**ANTES:**
```python
    context = {
        'contactos': contactos,
        'total_contactos': total_contactos,
        ...
    }

    return render(request, 'dashboard/contactos.html', context)
```

**DESPUÉS:**
```python
    # Paginación (agregar ANTES del context)
    paginator = Paginator(contactos, 30)  # 30 contactos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'contactos': page_obj,  # Cambiar contactos por page_obj
        'total_contactos': total_contactos,
        ...
    }

    return render(request, 'dashboard/contactos.html', context)
```

## Actualización de Templates

Los templates de Django necesitan usar el objeto de paginación. Ejemplo:

### En `dashboard/users.html`, `dashboard/articulos.html`, `dashboard/contactos.html`:

Agregar al final de la tabla (antes del cierre del contenedor):

```html
<!-- Paginación -->
{% if users.has_other_pages %}
<div class="pagination">
    <span class="step-links">
        {% if users.has_previous %}
            <a href="?page=1">&laquo; primera</a>
            <a href="?page={{ users.previous_page_number }}">anterior</a>
        {% endif %}

        <span class="current-page">
            Página {{ users.number }} de {{ users.paginator.num_pages }}
        </span>

        {% if users.has_next %}
            <a href="?page={{ users.next_page_number }}">siguiente</a>
            <a href="?page={{ users.paginator.num_pages }}">última &raquo;</a>
        {% endif %}
    </span>
</div>
{% endif %}
```

**Nota:** Cambiar `users` por `articulos` o `contactos` según corresponda.

## Archivos a Modificar

1. `backend/dashboard/views.py` - Agregar paginación en Python
2. `backend/dashboard/templates/dashboard/users.html` - Agregar HTML de paginación
3. `backend/dashboard/templates/dashboard/articulos.html` - Agregar HTML de paginación
4. `backend/dashboard/templates/dashboard/contactos.html` - Agregar HTML de paginación

## Verificación

Después de aplicar los cambios, verificar:

1. Que las páginas cargan correctamente
2. Que los botones de paginación funcionan
3. Que los filtros se mantienen al cambiar de página
4. Que los contadores muestran totales correctos

## Respaldo

Se creó respaldo en:
- `backend/dashboard/views.py.bak`

Para restaurar:
```bash
cp backend/dashboard/views.py.bak backend/dashboard/views.py
```
