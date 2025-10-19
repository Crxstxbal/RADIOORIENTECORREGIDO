from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from datetime import datetime, timedelta
import json

from apps.users.models import User
from apps.articulos.models import Articulo, Categoria
from apps.radio.models import Programa, EstacionRadio, HorarioPrograma, GeneroMusical
from apps.chat.models import ChatMessage
from apps.contact.models import Contacto, Suscripcion, Estado, TipoAsunto
from apps.emergente.models import BandaEmergente, BandaLink, Integrante, BandaIntegrante
from apps.ubicacion.models import Pais, Ciudad, Comuna


def is_staff_user(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_staff_user)
def dashboard_home(request):
    """Dashboard principal con métricas generales"""
    # Estadísticas generales
    total_users = User.objects.count()
    total_posts = Articulo.objects.count()
    total_programs = Programa.objects.count()
    total_subscriptions = Suscripcion.objects.count()
    
    # Estadísticas de la última semana
    last_week = timezone.now() - timedelta(days=7)
    new_users_week = User.objects.filter(fecha_creacion__gte=last_week).count()
    new_posts_week = Articulo.objects.filter(fecha_creacion__gte=last_week).count()
    new_messages_week = ChatMessage.objects.filter(fecha_envio__gte=last_week).count()
    
    # Artículos más populares (por fecha de publicación reciente)
    popular_posts = Articulo.objects.filter(publicado=True).order_by('-fecha_publicacion')[:5]
    
    # Mensajes de contacto recientes
    recent_contacts = Contacto.objects.order_by('-fecha_envio')[:5]
    
    context = {
        'total_users': total_users,
        'total_posts': total_posts,
        'total_programs': total_programs,
        'total_subscriptions': total_subscriptions,
        'new_users_week': new_users_week,
        'new_posts_week': new_posts_week,
        'new_messages_week': new_messages_week,
        'popular_posts': popular_posts,
        'recent_contacts': recent_contacts,
    }
    
    return render(request, 'dashboard/home.html', context)

@login_required
@user_passes_test(is_staff_user)
def dashboard_users(request):
    """Gestión de usuarios"""
    users = User.objects.all().order_by('-fecha_creacion')
    return render(request, 'dashboard/users.html', {'users': users})

@login_required
@user_passes_test(is_staff_user)
def dashboard_articulos(request):
    """Gestión de artículos"""
    articulos = Articulo.objects.select_related('autor', 'categoria').all().order_by('-fecha_creacion')
    categorias = Categoria.objects.all().order_by('nombre')
    return render(request, 'dashboard/articulos.html', {'articulos': articulos, 'categorias': categorias})

@login_required
@user_passes_test(is_staff_user)
def dashboard_radio(request):
    """Gestión de radio y programas"""
    programs = Programa.objects.all().order_by('nombre')
    try:
        station = EstacionRadio.objects.first()
    except EstacionRadio.DoesNotExist:
        station = None
    
    context = {
        'programs': programs,
        'station': station,
    }
    return render(request, 'dashboard/radio.html', context)

@login_required
@user_passes_test(is_staff_user)
def dashboard_chat(request):
    """Moderación del chat"""
    messages = ChatMessage.objects.all().order_by('-fecha_envio')[:50]
    return render(request, 'dashboard/chat.html', {'messages': messages})

@login_required
@user_passes_test(is_staff_user)
def dashboard_analytics(request):
    """Analytics y estadísticas detalladas"""
    # Datos para gráficos
    last_30_days = timezone.now() - timedelta(days=30)
    
    # Usuarios por día (últimos 30 días)
    users_by_day = []
    for i in range(30):
        date = timezone.now() - timedelta(days=i)
        count = User.objects.filter(fecha_creacion__date=date.date()).count()
        users_by_day.append({'date': date.strftime('%Y-%m-%d'), 'count': count})
    
    # Posts por mes (últimos 6 meses)
    posts_by_month = []
    for i in range(6):
        date = timezone.now() - timedelta(days=30*i)
        count = Articulo.objects.filter(
            fecha_creacion__year=date.year,
            fecha_creacion__month=date.month
        ).count()
        posts_by_month.append({'month': date.strftime('%Y-%m'), 'count': count})
    
    context = {
        'users_by_day': users_by_day,
        'posts_by_month': posts_by_month,
    }
    
    return render(request, 'dashboard/analytics.html', context)

def dashboard_login(request):
    """Login específico para el dashboard"""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard_home')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user and user.is_staff:
            login(request, user)
            return redirect('dashboard_home')
        else:
            return render(request, 'dashboard/login.html', {
                'error': 'Credenciales inválidas o sin permisos de administrador'
            })
    
    return render(request, 'dashboard/login.html')

def dashboard_logout(request):
    """Logout del dashboard"""
    logout(request)
    return redirect('dashboard_login')

@login_required
@user_passes_test(is_staff_user)
def api_dashboard_stats(request):
    """API endpoint para estadísticas del dashboard"""
    stats = {
        'users': User.objects.count(),
        'posts': Articulo.objects.count(),
        'programs': Programa.objects.count(),
        'messages': ChatMessage.objects.count(),
        'subscriptions': Suscripcion.objects.count(),
    }
    return JsonResponse(stats)

# CRUD Operations for Users
@login_required
@user_passes_test(is_staff_user)
def create_user(request):
    """Crear nuevo usuario"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        usuario = request.POST.get('usuario')
        correo = request.POST.get('correo')
        password = request.POST.get('password')
        is_staff = request.POST.get('is_staff') == 'on'
        
        try:
            user = User.objects.create_user(
                email=correo,
                username=usuario,
                password=password,
                first_name=nombre,
                is_staff=is_staff
            )
            messages.success(request, f'Usuario {usuario} creado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al crear usuario: {str(e)}')
    
    return redirect('dashboard_users')

@login_required
@user_passes_test(is_staff_user)
def edit_user(request, user_id):
    """Editar usuario existente"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.nombre = request.POST.get('nombre')
        user.usuario = request.POST.get('usuario')
        user.correo = request.POST.get('correo')
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.is_active = request.POST.get('is_active') == 'on'
        
        password = request.POST.get('password')
        if password:
            user.set_password(password)
        
        try:
            user.save()
            messages.success(request, f'Usuario {user.usuario} actualizado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al actualizar usuario: {str(e)}')
    
    return redirect('dashboard_users')

@login_required
@user_passes_test(is_staff_user)
def delete_user(request, user_id):
    """Eliminar usuario"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        username = user.usuario
        try:
            user.delete()
            messages.success(request, f'Usuario {username} eliminado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar usuario: {str(e)}')
    
    return redirect('dashboard_users')

# CRUD Operations for Articulos
@login_required
@user_passes_test(is_staff_user)
def create_articulo(request):
    """Crear nuevo artículo con soporte multimedia"""
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        contenido = request.POST.get('contenido')
        resumen = request.POST.get('resumen')
        categoria = request.POST.get('categoria')
        publicado = request.POST.get('publicado') == 'on'
        imagen_url = request.POST.get('imagen_url')
        video_url = request.POST.get('video_url')
        
        # Obtener archivos subidos
        imagen_portada = request.FILES.get('imagen_portada')
        imagen_thumbnail = request.FILES.get('imagen_thumbnail')
        archivo_adjunto = request.FILES.get('archivo_adjunto')
        
        try:
            # Obtener la categoría por ID
            if categoria:
                categoria_obj = Categoria.objects.get(id=categoria)
            else:
                # Crear categoría por defecto si no existe
                categoria_obj, _ = Categoria.objects.get_or_create(
                    nombre='General',
                    defaults={'descripcion': 'Categoría general'}
                )
            
            articulo = Articulo.objects.create(
                titulo=titulo,
                contenido=contenido,
                resumen=resumen,
                categoria=categoria_obj,
                publicado=publicado,
                imagen_url=imagen_url,
                video_url=video_url,
                imagen_portada=imagen_portada,
                imagen_thumbnail=imagen_thumbnail,
                archivo_adjunto=archivo_adjunto,
                autor=request.user
            )
            messages.success(request, f'Artículo "{titulo}" creado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al crear artículo: {str(e)}')
    
    return redirect('dashboard_articulos')

@login_required
@user_passes_test(is_staff_user)
def edit_articulo(request, articulo_id):
    """Editar artículo con soporte multimedia"""
    articulo = get_object_or_404(Articulo, id=articulo_id)
    
    if request.method == 'POST':
        articulo.titulo = request.POST.get('titulo')
        articulo.contenido = request.POST.get('contenido')
        articulo.resumen = request.POST.get('resumen')
        categoria_id = request.POST.get('categoria')
        articulo.publicado = request.POST.get('publicado') == 'on'
        articulo.imagen_url = request.POST.get('imagen_url')
        articulo.video_url = request.POST.get('video_url')
        
        # Actualizar archivos si se proporcionan nuevos
        imagen_portada = request.FILES.get('imagen_portada')
        if imagen_portada:
            articulo.imagen_portada = imagen_portada
        
        imagen_thumbnail = request.FILES.get('imagen_thumbnail')
        if imagen_thumbnail:
            articulo.imagen_thumbnail = imagen_thumbnail
            
        archivo_adjunto = request.FILES.get('archivo_adjunto')
        if archivo_adjunto:
            articulo.archivo_adjunto = archivo_adjunto
        
        try:
            # Actualizar categoría si se proporciona
            if categoria_id:
                articulo.categoria = Categoria.objects.get(id=categoria_id)
            articulo.save()
            messages.success(request, f'Artículo "{articulo.titulo}" actualizado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al actualizar artículo: {str(e)}')
    
    return redirect('dashboard_articulos')

@login_required
@user_passes_test(is_staff_user)
def delete_articulo(request, articulo_id):
    """Eliminar artículo"""
    articulo = get_object_or_404(Articulo, id=articulo_id)
    
    if request.method == 'POST':
        titulo = articulo.titulo
        try:
            articulo.delete()
            messages.success(request, f'Artículo "{titulo}" eliminado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar artículo: {str(e)}')
    
    return redirect('dashboard_articulos')

# CRUD Operations for Radio Programs
@login_required
@user_passes_test(is_staff_user)
def create_program(request):
    """Crear nuevo programa de radio"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')
        dias = request.POST.getlist('dias[]')  # Obtener lista de días seleccionados
        activo = request.POST.get('activo') == 'on'
        
        try:
            # Crear el programa
            program = Programa.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                activo=activo
            )
            
            # Crear horarios para cada día seleccionado
            if dias and hora_inicio and hora_fin:
                for dia in dias:
                    HorarioPrograma.objects.create(
                        programa=program,
                        dia_semana=int(dia),
                        hora_inicio=hora_inicio,
                        hora_fin=hora_fin,
                        activo=True
                    )
            
            messages.success(request, f'Programa "{nombre}" creado exitosamente con {len(dias)} horarios')
        except Exception as e:
            messages.error(request, f'Error al crear programa: {str(e)}')
    
    return redirect('dashboard_radio')

@login_required
@user_passes_test(is_staff_user)
def edit_program(request, program_id):
    """Editar programa de radio"""
    program = get_object_or_404(Programa, id=program_id)
    
    if request.method == 'POST':
        program.nombre = request.POST.get('nombre')
        program.descripcion = request.POST.get('descripcion')
        program.activo = request.POST.get('activo') == 'on'
        
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')
        dias = request.POST.getlist('dias[]')
        
        try:
            program.save()
            
            # Actualizar horarios: eliminar los existentes y crear nuevos
            if dias and hora_inicio and hora_fin:
                # Eliminar horarios antiguos
                program.horarios.all().delete()
                
                # Crear nuevos horarios
                for dia in dias:
                    HorarioPrograma.objects.create(
                        programa=program,
                        dia_semana=int(dia),
                        hora_inicio=hora_inicio,
                        hora_fin=hora_fin,
                        activo=True
                    )
            
            messages.success(request, f'Programa "{program.nombre}" actualizado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al actualizar programa: {str(e)}')
    
    return redirect('dashboard_radio')

@login_required
@user_passes_test(is_staff_user)
def delete_program(request, program_id):
    """Eliminar programa de radio"""
    program = get_object_or_404(Programa, id=program_id)
    
    if request.method == 'POST':
        nombre = program.nombre
        try:
            program.delete()
            messages.success(request, f'Programa "{nombre}" eliminado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar programa: {str(e)}')
    
    return redirect('dashboard_radio')

# CRUD Operations for News
@login_required
@user_passes_test(is_staff_user)
def create_news(request):
    """Crear nueva noticia"""
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        contenido = request.POST.get('contenido')
        categoria = request.POST.get('categoria')
        imagen_url = request.POST.get('imagen_url')
        publicado = request.POST.get('publicado') == 'on'
        
        try:
            # Obtener categoría de noticias
            categoria_noticias = Categoria.objects.get_or_create(nombre='Noticias')[0]
            
            # Crear artículo de noticias
            news = Articulo.objects.create(
                titulo=titulo,
                contenido=contenido,
                categoria=categoria_noticias,
                imagen_url=imagen_url,
                publicado=publicado,
                autor=request.user
            )
            messages.success(request, f'Noticia "{titulo}" creada exitosamente')
        except Exception as e:
            messages.error(request, f'Error al crear noticia: {str(e)}')
    
    return redirect('dashboard_radio')

@login_required
@user_passes_test(is_staff_user)
def delete_news(request, news_id):
    """Eliminar noticia"""
    news = get_object_or_404(Articulo, id=news_id)
    
    if request.method == 'POST':
        titulo = news.titulo
        try:
            news.delete()
            messages.success(request, f'Noticia "{titulo}" eliminada exitosamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar noticia: {str(e)}')
    
    return redirect('dashboard_radio')

# Chat Moderation
@login_required
@user_passes_test(is_staff_user)
def delete_message(request, message_id):
    """Eliminar mensaje del chat"""
    message = get_object_or_404(ChatMessage, id=message_id)
    
    if request.method == 'POST':
        try:
            message.delete()
            messages.success(request, 'Mensaje eliminado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar mensaje: {str(e)}')
    
    return redirect('dashboard_chat')

@login_required
@user_passes_test(is_staff_user)
def update_station(request):
    """Actualizar configuración de la estación"""
    station = EstacionRadio.objects.first()
    
    if request.method == 'POST':
        station.nombre = request.POST.get('nombre', station.nombre)
        station.descripcion = request.POST.get('descripcion', station.descripcion)
        station.stream_url = request.POST.get('stream_url', station.stream_url)
        # Actualizar otros campos si existen en el formulario
        station.telefono = request.POST.get('telefono', station.telefono)
        station.email = request.POST.get('email', station.email)
        station.direccion = request.POST.get('direccion', station.direccion)
        
        station.save()
        messages.success(request, 'Configuración de estación actualizada exitosamente')
    
    return redirect('dashboard_radio')

# ===============================
# Bandas Emergentes (CRUD + Estado)
# ===============================
@login_required
@user_passes_test(is_staff_user)
def get_comunas_ajax(request):
    """Vista para obtener las comunas de una región mediante AJAX"""
    region_id = request.GET.get('region_id')
    if region_id:
        comunas = Comuna.objects.filter(region_id=region_id).order_by('nombre')
        data = {
            'comunas': [{'id': c.id, 'nombre': c.nombre} for c in comunas]
        }
        return JsonResponse(data)
    return JsonResponse({'error': 'No se proporcionó el ID de la región'}, status=400)

@login_required
@user_passes_test(is_staff_user)
def crear_banda_emergente(request):
    """Vista para crear una nueva banda emergente"""
    if request.method == 'POST':
        form = BandaEmergenteForm(request.POST, request.FILES)
        if form.is_valid():
            banda = form.save(commit=False)
            banda.usuario = request.user
            banda.save()
            messages.success(request, 'Banda creada exitosamente')
            return redirect('dashboard_emergentes')
    else:
        form = BandaEmergenteForm()
    
    return render(request, 'dashboard/emergentes/form_banda.html', {
        'form': form,
        'titulo': 'Nueva Banda Emergente'
    })

@login_required
@user_passes_test(is_staff_user)
def editar_banda_emergente(request, banda_id):
    """Vista para editar una banda emergente existente"""
    banda = get_object_or_404(BandaEmergente, id=banda_id)
    
    if request.method == 'POST':
        form = BandaEmergenteForm(request.POST, request.FILES, instance=banda)
        if form.is_valid():
            form.save()
            messages.success(request, 'Banda actualizada exitosamente')
            return redirect('dashboard_emergentes')
    else:
        form = BandaEmergenteForm(instance=banda)
    
    return render(request, 'dashboard/emergentes/form_banda.html', {
        'form': form,
        'titulo': f'Editar {banda.nombre_banda}'
    })

@login_required
@user_passes_test(is_staff_user)
def dashboard_emergentes(request):
    """Gestión de bandas emergentes"""
    # Obtener todas las bandas con sus relaciones
    bandas = BandaEmergente.objects.select_related(
        'genero', 'usuario', 'estado', 'comuna', 'comuna__ciudad', 'comuna__ciudad__pais'
    ).prefetch_related('integrantes__integrante', 'links').order_by('-fecha_envio')
    
    # Filtros
    estado = request.GET.get('estado')
    genero = request.GET.get('genero')
    busqueda = request.GET.get('q')
    
    if estado:
        bandas = bandas.filter(estado__nombre=estado)
    
    if genero:
        bandas = bandas.filter(genero_id=genero)
    
    if busqueda:
        bandas = bandas.filter(
            Q(nombre_banda__icontains=busqueda) |
            Q(email_contacto__icontains=busqueda) |
            Q(comuna__nombre__icontains=busqueda) |
            Q(comuna__ciudad__nombre__icontains=busqueda)
        )
    
    # Obtener estadísticas de estados para el filtro
    stats_estados = BandaEmergente.objects.values('estado__nombre').annotate(
        total=Count('id')
    ).order_by('estado__nombre')
    
    # Convertir a diccionario para el template
    stats_estados = {item['estado__nombre']: item['total'] for item in stats_estados}
    
    # Paginación
    paginator = Paginator(bandas, 20)  # 20 bandas por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obtener géneros para el filtro
    generos = GeneroMusical.objects.filter(bandas_emergentes__isnull=False).distinct()
    
    context = {
        'bandas': page_obj,
        'total_bandas': paginator.count,
        'estados': Estado.objects.all(),
        'generos': generos,
        'estado_actual': estado,
        'genero_actual': int(genero) if genero and genero.isdigit() else None,
        'busqueda': busqueda or '',
        'stats_estados': stats_estados,
    }
    
    return render(request, 'dashboard/emergente.html', context)

@login_required
@user_passes_test(is_staff_user)
def cambiar_estado_banda(request, banda_id, nuevo_estado):
    """Cambiar el estado de una banda usando la tabla Estado normalizada"""
    banda = get_object_or_404(BandaEmergente, id=banda_id)
    
    # Mapear nombres de estados a los de la base de datos
    estados_mapping = {
        'aprobado': 'Aprobada',
        'rechazado': 'Rechazada',
        'pendiente': 'Recibida',
        'revision': 'En Revisión'
    }
    
    nombre_estado = estados_mapping.get(nuevo_estado, nuevo_estado)
    
    try:
        # Buscar el estado en la tabla Estado
        estado_obj = Estado.objects.get(
            nombre__iexact=nombre_estado,
            tipo_entidad='banda'
        )
        
        banda.estado = estado_obj
        banda.revisado_por = request.user
        banda.fecha_revision = timezone.now()
        banda.save()
        
        messages.success(request, f"Estado de '{banda.nombre_banda}' actualizado a {estado_obj.nombre}.")
    except Estado.DoesNotExist:
        messages.error(request, f"Estado '{nombre_estado}' no encontrado.")
    except Exception as e:
        messages.error(request, f"Error al actualizar estado: {str(e)}")
    
    return redirect('dashboard_emergentes')


@login_required
@user_passes_test(is_staff_user)
def view_banda(request, banda_id):
    """Ver detalle completo de una banda emergente"""
    banda = get_object_or_404(BandaEmergente, id=banda_id)
    return render(request, 'dashboard/emergente_detail.html', {'banda': banda})


@login_required
@user_passes_test(is_staff_user)
def eliminar_banda_emergente(request, banda_id):
    """Eliminar banda emergente"""
    if request.method != 'POST':
        return redirect('dashboard_emergentes')

    try:
        banda = BandaEmergente.objects.get(id=banda_id)
        nombre_banda = banda.nombre_banda
        banda.delete()
        messages.success(request, f'Banda "{nombre_banda}" eliminada correctamente.')
    except BandaEmergente.DoesNotExist:
        messages.error(request, 'La banda no existe.')
    except Exception as e:
        messages.error(request, f'Error al eliminar: {str(e)}')

    return redirect('dashboard_emergentes')


# Las vistas para crear y editar bandas emergentes se manejarán en el frontend
@login_required
@user_passes_test(is_staff_user)
@require_http_methods(["POST"])
def agregar_genero(request):
    """Agregar un nuevo género musical"""
    nombre = request.POST.get('nombre')
    descripcion = request.POST.get('descripcion', '')
    
    if not nombre:
        messages.error(request, 'El nombre del género es obligatorio.')
        return redirect('dashboard_emergentes')
    
    try:
        # Verificar si ya existe un género con el mismo nombre (insensible a mayúsculas/minúsculas)
        if GeneroMusical.objects.filter(nombre__iexact=nombre).exists():
            messages.warning(request, f'El género "{nombre}" ya existe.')
        else:
            # Crear el nuevo género
            genero = GeneroMusical.objects.create(
                nombre=nombre,
                descripcion=descripcion
            )
            messages.success(request, f'Género "{genero.nombre}" creado exitosamente.')
    except Exception as e:
        messages.error(request, f'Error al crear el género: {str(e)}')
    
    return redirect('dashboard_emergentes')


@login_required
@user_passes_test(is_staff_user)
def eliminar_genero(request, genero_id):
    """Eliminar un género musical"""
    if request.method != 'POST':
        messages.error(request, 'Método no permitido')
        return redirect('dashboard_emergentes')
        
    try:
        genero = GeneroMusical.objects.get(id=genero_id)
        nombre_genero = genero.nombre
        
        # Verificar si hay bandas usando este género
        if genero.bandas_emergentes.exists():
            # Eliminar pero mantener la relación
            genero.delete()
            messages.success(request, f'Género "{nombre_genero}" eliminado. Las bandas existentes mantendrán este género.')
        else:
            genero.delete()
            messages.success(request, f'Género "{nombre_genero}" eliminado correctamente.')
            
    except GeneroMusical.DoesNotExist:
        messages.error(request, 'El género no existe o ya ha sido eliminado.')
    except Exception as e:
        messages.error(request, f'Error al eliminar el género: {str(e)}')
    
    return redirect('dashboard_emergentes')


# ===============================
# Contactos (CRUD + Estado)
# ===============================
@login_required
@user_passes_test(is_staff_user)
def dashboard_contactos(request):
    """Gestión de contactos"""
    # Obtener parámetros de filtro
    estado_filter = request.GET.get('estado')
    tipo_filter = request.GET.get('tipo')
    search_query = request.GET.get('q')

    # Query base
    contactos = Contacto.objects.select_related(
        'tipo_asunto', 'estado', 'usuario', 'respondido_por'
    ).order_by('-fecha_envio')

    # Aplicar filtros
    if estado_filter:
        contactos = contactos.filter(estado_id=estado_filter)
    if tipo_filter:
        contactos = contactos.filter(tipo_asunto_id=tipo_filter)
    if search_query:
        contactos = contactos.filter(
            Q(nombre__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(mensaje__icontains=search_query)
        )

    # Estadísticas
    total_contactos = Contacto.objects.count()

    # Contactos pendientes (estado Recibida o Pendiente)
    contactos_pendientes = Contacto.objects.filter(
        Q(estado__nombre__iexact='Recibida') | Q(estado__nombre__iexact='Pendiente')
    ).count()

    # Contactos respondidos
    contactos_respondidos = Contacto.objects.filter(
        estado__nombre__iexact='Respondida'
    ).count()

    # Contactos de esta semana
    last_week = timezone.now() - timedelta(days=7)
    contactos_semana = Contacto.objects.filter(fecha_envio__gte=last_week).count()

    # Obtener estados y tipos de asunto disponibles
    estados_disponibles = Estado.objects.filter(tipo_entidad='contacto').order_by('nombre')
    tipos_asunto = TipoAsunto.objects.all().order_by('nombre')

    context = {
        'contactos': contactos,
        'total_contactos': total_contactos,
        'contactos_pendientes': contactos_pendientes,
        'contactos_respondidos': contactos_respondidos,
        'contactos_semana': contactos_semana,
        'estados_disponibles': estados_disponibles,
        'tipos_asunto': tipos_asunto,
    }

    return render(request, 'dashboard/contactos.html', context)


@login_required
@user_passes_test(is_staff_user)
def update_contacto(request, contacto_id):
    """Actualizar estado de un contacto"""
    contacto = get_object_or_404(Contacto, id=contacto_id)

    if request.method == 'POST':
        nuevo_estado_id = request.POST.get('estado')

        try:
            nuevo_estado = Estado.objects.get(id=nuevo_estado_id, tipo_entidad='contacto')
            contacto.estado = nuevo_estado

            # Si el estado es "Respondida", marcar fecha y usuario
            if nuevo_estado.nombre.lower() == 'respondida':
                contacto.fecha_respuesta = timezone.now()
                contacto.respondido_por = request.user

            contacto.save()
            messages.success(request, f"Estado del contacto actualizado a '{nuevo_estado.nombre}'.")
        except Estado.DoesNotExist:
            messages.error(request, "Estado no encontrado.")
        except Exception as e:
            messages.error(request, f"Error al actualizar contacto: {str(e)}")

    return redirect('dashboard_contactos')


@login_required
@user_passes_test(is_staff_user)
def delete_contacto(request, contacto_id):
    """Eliminar un contacto"""
    contacto = get_object_or_404(Contacto, id=contacto_id)

    if request.method == 'POST':
        nombre = contacto.nombre
        try:
            contacto.delete()
            messages.success(request, f"Contacto de '{nombre}' eliminado exitosamente.")
        except Exception as e:
            messages.error(request, f"Error al eliminar contacto: {str(e)}")

    return redirect('dashboard_contactos')
