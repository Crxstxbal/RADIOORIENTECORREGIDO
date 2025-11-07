from datetime import datetime
from datetime import timezone as dt_timezone
import traceback
from django.conf import settings
from django.http import JsonResponse
from google.oauth2 import service_account
from googleapiclient.discovery import build

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

from .forms import BandaEmergenteForm

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
def dashboard_calendario(request):
    context = {} 
    return render(request, 'dashboard/calendario.html', context)

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

@login_required
@user_passes_test(is_staff_user)
@require_http_methods(["POST"])
def agregar_categoria(request):
    """Agregar una nueva categoría de artículo, con soporte para AJAX y fallback."""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    nombre = request.POST.get('nombre')
    descripcion = request.POST.get('descripcion', '')

    if not nombre:
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': 'El nombre de la categoría es obligatorio.'}, status=400)
        messages.error(request, 'El nombre de la categoría es obligatorio.')
        return redirect('dashboard_articulos')

    try:
        if Categoria.objects.filter(nombre__iexact=nombre).exists():
            message = f'La categoría "{nombre}" ya existe.'
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': message}, status=400)
            messages.warning(request, message)
        else:
            categoria = Categoria.objects.create(nombre=nombre, descripcion=descripcion)
            message = f'Categoría "{categoria.nombre}" creada exitosamente.'
            if is_ajax:
                return JsonResponse({
                    'status': 'success',
                    'message': message,
                    'categoria': {
                        'id': categoria.id,
                        'nombre': categoria.nombre,
                        'descripcion': categoria.descripcion or ''
                    }
                })
            messages.success(request, message)
    except Exception as e:
        message = f'Error al crear la categoría: {str(e)}'
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': message}, status=500)
        messages.error(request, message)

    return redirect('dashboard_articulos')


@login_required
@user_passes_test(is_staff_user)
@require_http_methods(["POST"])
def eliminar_categoria(request, categoria_id):
    """Eliminar una categoría de artículo, con soporte para AJAX y fallback."""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    try:
        categoria = get_object_or_404(Categoria, id=categoria_id)
        nombre_categoria = categoria.nombre
        
        # Verificar si hay artículos usando esta categoría
        if Articulo.objects.filter(categoria=categoria).exists():
            message = f'No se puede eliminar la categoría "{nombre_categoria}" porque tiene artículos asociados.'
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': message}, status=400)
            messages.error(request, message)
            return redirect('dashboard_articulos')
            
        categoria.delete()
        message = f'Categoría "{nombre_categoria}" eliminada correctamente.'

        if is_ajax:
            return JsonResponse({'status': 'success', 'message': message})
        
        messages.success(request, message)

    except Exception as e:
        message = f'Error al eliminar la categoría: {str(e)}'
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': message}, status=500)
        messages.error(request, message)
    
    return redirect('dashboard_articulos')

@login_required
@user_passes_test(is_staff_user)
def dashboard_radio(request):
    """Gestión de radio y programas"""
    programs = Programa.objects.all().order_by('nombre')
    try:
        station = EstacionRadio.objects.first()
    except EstacionRadio.DoesNotExist:
        station = None
    
    # Obtener los 3 artículos más recientes
    articulos_recientes = Articulo.objects.filter(
        publicado=True
    ).select_related('categoria', 'autor').order_by('-fecha_publicacion')[:3]
    
    # Obtener el total de artículos
    total_articulos = Articulo.objects.count()
    
    context = {
        'programs': programs,
        'station': station,
        'articulos_recientes': articulos_recientes,
        'total_articulos': total_articulos,
        'total_articulos_count': total_articulos  # Adding this for the statistics section
    }
    return render(request, 'dashboard/radio.html', context)

@login_required
@user_passes_test(is_staff_user)
def dashboard_chat(request):
    """Moderación del chat"""
    # Obtener todos los mensajes
    messages = ChatMessage.objects.all().order_by('-fecha_envio')[:50]

    # Calcular estadísticas usando timezone aware datetime
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    messages_today = ChatMessage.objects.filter(
        fecha_envio__gte=today_start,
        fecha_envio__lte=today_end
    ).count()

    # Usuarios únicos activos hoy (basado en mensajes)
    active_users_today = ChatMessage.objects.filter(
        fecha_envio__gte=today_start,
        fecha_envio__lte=today_end
    ).values('id_usuario').distinct().count()

    context = {
        'messages': messages,
        'messages_today': messages_today,
        'active_users_today': active_users_today,
    }

    return render(request, 'dashboard/chat.html', context)

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

# Estado CRUD
@login_required
@user_passes_test(is_staff_user)
@require_http_methods(["POST"])
def agregar_estado(request):
    """Agregar un nuevo estado, con soporte para AJAX y fallback."""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    nombre = request.POST.get('nombre')
    descripcion = request.POST.get('descripcion', '')
    tipo_entidad = request.POST.get('tipo_entidad')

    if not nombre or not tipo_entidad:
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': 'El nombre y tipo de estado son obligatorios.'}, status=400)
        messages.error(request, 'El nombre y tipo de estado son obligatorios.')
        return redirect('dashboard_emergentes')

    try:
        if Estado.objects.filter(nombre__iexact=nombre, tipo_entidad=tipo_entidad).exists():
            message = f'El estado "{nombre}" ya existe para {tipo_entidad}.'
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': message}, status=400)
            messages.warning(request, message)
        else:
            estado = Estado.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                tipo_entidad=tipo_entidad
            )
            message = f'Estado "{estado.nombre}" creado exitosamente.'
            if is_ajax:
                return JsonResponse({
                    'status': 'success',
                    'message': message,
                    'estado': {
                        'id': estado.id,
                        'nombre': estado.nombre,
                        'descripcion': estado.descripcion,
                        'tipo_entidad': estado.tipo_entidad
                    }
                })
            messages.success(request, message)
    except Exception as e:
        message = f'Error al crear el estado: {str(e)}'
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': message}, status=500)
        messages.error(request, message)

    return redirect('dashboard_emergentes')

@login_required
@user_passes_test(is_staff_user)
@require_http_methods(["POST"])
def eliminar_estado(request, estado_id):
    """Eliminar un estado, con soporte para AJAX y fallback."""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    try:
        estado = get_object_or_404(Estado, id=estado_id)
        nombre_estado = estado.nombre

        # Verificar si hay elementos usando este estado
        if estado.tipo_entidad == 'contacto' and estado.contactos.exists():
            message = f'No se puede eliminar el estado "{nombre_estado}" porque está siendo usado por contactos.'
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': message}, status=400)
            messages.error(request, message)
            return redirect('dashboard_emergentes')

        if estado.tipo_entidad == 'banda' and BandaEmergente.objects.filter(estado=estado).exists():
            message = f'No se puede eliminar el estado "{nombre_estado}" porque está siendo usado por bandas.'
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': message}, status=400)
            messages.error(request, message)
            return redirect('dashboard_emergentes')

        estado.delete()
        message = f'Estado "{nombre_estado}" eliminado correctamente.'

        if is_ajax:
            return JsonResponse({'status': 'success', 'message': message})
        messages.success(request, message)

    except Exception as e:
        message = f'Error al eliminar el estado: {str(e)}'
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': message}, status=500)
        messages.error(request, message)

    return redirect('dashboard_emergentes')

# Chat Moderation
@login_required
@user_passes_test(is_staff_user)
def delete_message(request, message_id):
    """Eliminar mensaje del chat"""
    if request.method == 'POST':
        try:
            message = get_object_or_404(ChatMessage, id=message_id)
            message.delete()
            messages.success(request, 'Mensaje eliminado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar el mensaje: {str(e)}')
    
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

@login_required
@user_passes_test(is_staff_user)
def toggle_station_status(request):
    """Alternar el estado de la estación (activo/inactivo)"""
    if request.method == 'POST':
        try:
            station = EstacionRadio.objects.first()
            if station:
                station.activo = not station.activo
                station.save()
                status = 'activa' if station.activo else 'en pausa'
                messages.success(request, f'La transmisión está ahora {status}')
            else:
                messages.error(request, 'No se encontró la estación de radio')
        except Exception as e:
            messages.error(request, f'Error al cambiar el estado: {str(e)}')
    
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
    
    # Obtener todos los géneros para el filtro y la gestión
    generos = GeneroMusical.objects.all().order_by('nombre')
    
    context = {
        'bandas': page_obj,
        'total_bandas': paginator.count,
        'estados': Estado.objects.all().order_by('tipo_entidad', 'nombre'),
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
    """Cambiar el estado de una banda y registrar quién lo revisó"""
    banda = get_object_or_404(BandaEmergente, id=banda_id)
    
    try:
        # Mapeo de estados (de la URL a los nombres en la BD)
        estados_mapping = {
            'pendiente': 'Pendiente',
            'aprobado': 'Aprobado', 
            'rechazado': 'Rechazado',
            'revision': 'Revisado'
        }
        
        # Buscar el estado en la tabla Estado
        nombre_estado = estados_mapping.get(nuevo_estado.lower(), nuevo_estado)
        estado_obj = Estado.objects.get(
            nombre=nombre_estado,
            tipo_entidad='banda'
        )
        
        # Actualizar estado y registrar quién lo revisó
        banda.estado = estado_obj
        banda.revisado_por = request.user
        banda.fecha_revision = timezone.now()
        banda.save()
        
        messages.success(request, f"Estado de '{banda.nombre_banda}' actualizado a {estado_obj.nombre}.")
    except Estado.DoesNotExist:
        messages.error(request, f"Estado '{nuevo_estado}' no encontrado.")
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
    """Agregar un nuevo género musical, con soporte para AJAX y fallback."""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    nombre = request.POST.get('nombre')
    descripcion = request.POST.get('descripcion', '')

    if not nombre:
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': 'El nombre del género es obligatorio.'}, status=400)
        messages.error(request, 'El nombre del género es obligatorio.')
        return redirect('dashboard_emergentes')

    try:
        if GeneroMusical.objects.filter(nombre__iexact=nombre).exists():
            message = f'El género "{nombre}" ya existe.'
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': message}, status=400)
            messages.warning(request, message)
        else:
            genero = GeneroMusical.objects.create(nombre=nombre, descripcion=descripcion)
            message = f'Género "{genero.nombre}" creado exitosamente.'
            if is_ajax:
                return JsonResponse({
                    'status': 'success',
                    'message': message,
                    'genero': {
                        'id': genero.id,
                        'nombre': genero.nombre,
                        'descripcion': genero.descripcion
                    }
                })
            messages.success(request, message)
    except Exception as e:
        message = f'Error al crear el género: {str(e)}'
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': message}, status=500)
        messages.error(request, message)

    return redirect('dashboard_emergentes')


@login_required
@user_passes_test(is_staff_user)
@require_http_methods(["POST"])
def eliminar_genero(request, genero_id):
    """Eliminar un género musical, con soporte para AJAX y fallback."""
    is_ajax = request.headers.get('X-Requested-with') == 'XMLHttpRequest'

    try:
        genero = get_object_or_404(GeneroMusical, id=genero_id)
        nombre_genero = genero.nombre
        genero.delete()
        message = f'Género "{nombre_genero}" eliminado correctamente.'

        if is_ajax:
            return JsonResponse({'status': 'success', 'message': message})
        
        messages.success(request, message)

    except Exception as e:
        message = f'Error al eliminar el género: {str(e)}'
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': message}, status=500)
        messages.error(request, message)
    
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
        'estados': Estado.objects.all().order_by('tipo_entidad', 'nombre'),  # Añadido para la gestión de estados
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
def agregar_tipo_asunto(request):
    """
    Agregar un nuevo tipo de asunto, con soporte para AJAX y fallback.
    """
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        
        if not nombre:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'El nombre del tipo de asunto es requerido'}, status=400)
            messages.error(request, 'El nombre del tipo de asunto es requerido.')
            return redirect('dashboard_contactos')
        
        try:
            # Verificar si ya existe un tipo con el mismo nombre
            if TipoAsunto.objects.filter(nombre__iexact=nombre).exists():
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Ya existe un tipo de asunto con este nombre'}, status=400)
                messages.error(request, 'Ya existe un tipo de asunto con este nombre.')
                return redirect('dashboard_contactos')
            
            # Crear el nuevo tipo de asunto
            tipo = TipoAsunto.objects.create(
                nombre=nombre,
                descripcion=descripcion if descripcion else None
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'tipo': {
                        'id': tipo.id,
                        'nombre': tipo.nombre,
                        'descripcion': tipo.descripcion or ''
                    }
                })
            
            messages.success(request, f'Tipo de asunto "{tipo.nombre}" agregado correctamente.')
            return redirect('dashboard_contactos')
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
            messages.error(request, f'Error al agregar el tipo de asunto: {str(e)}')
            return redirect('dashboard_contactos')
    
    # Si no es una petición POST, redirigir al dashboard
    return redirect('dashboard_contactos')


@login_required
@user_passes_test(is_staff_user)
def eliminar_tipo_asunto(request, tipo_id):
    """
    Eliminar un tipo de asunto, con soporte para AJAX y fallback.
    """
    if request.method != 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
        messages.error(request, 'Método no permitido.')
        return redirect('dashboard_contactos')
    
    try:
        # Obtener el tipo de asunto
        tipo = TipoAsunto.objects.get(id=tipo_id)
        nombre_tipo = tipo.nombre
        
        # Verificar si hay contactos usando este tipo de asunto
        if Contacto.objects.filter(tipo_asunto=tipo).exists():
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False, 
                    'error': 'No se puede eliminar este tipo de asunto porque está siendo utilizado por uno o más contactos.'
                }, status=400)
            messages.error(request, 'No se puede eliminar este tipo de asunto porque está siendo utilizado por uno o más contactos.')
            return redirect('dashboard_contactos')
        
        # Eliminar el tipo de asunto
        tipo.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        messages.success(request, f'Tipo de asunto "{nombre_tipo}" eliminado correctamente.')
        return redirect('dashboard_contactos')
        
    except TipoAsunto.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'El tipo de asunto no existe'}, status=404)
        messages.error(request, 'El tipo de asunto no existe.')
        return redirect('dashboard_contactos')
        
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        messages.error(request, f'Error al eliminar el tipo de asunto: {str(e)}')
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

# ============================================
# NOTIFICACIONES
# ============================================

@login_required
@user_passes_test(is_staff_user)
def dashboard_notificaciones(request):
    """Vista principal de notificaciones"""
    from apps.notifications.models import Notification
    
    # Obtener filtros
    filtro_tipo = request.GET.get('tipo', '')
    filtro_leidas = request.GET.get('leidas', '')
    
    # Query base - solo notificaciones del usuario actual
    notificaciones = Notification.objects.filter(usuario=request.user).order_by("-fecha_creacion")
    
    # Aplicar filtros
    if filtro_tipo:
        notificaciones = notificaciones.filter(tipo=filtro_tipo)
    
    if filtro_leidas == 'si':
        notificaciones = notificaciones.filter(leido=True)
    elif filtro_leidas == 'no':
        notificaciones = notificaciones.filter(leido=False)
    
    # Paginación
    paginator = Paginator(notificaciones, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas
    total_notificaciones = notificaciones.count()
    no_leidas = notificaciones.filter(leido=False).count()
    leidas = notificaciones.filter(leido=True).count()

    context = {
        'page_obj': page_obj,
        'filtro_tipo': filtro_tipo,
        'filtro_leidas': filtro_leidas,
        'total_notificaciones': total_notificaciones,
        'no_leidas': no_leidas,
        'leidas': leidas,
    }
    
    return render(request, 'dashboard/notificaciones.html', context)


@login_required
@user_passes_test(is_staff_user)
@require_http_methods(['POST'])
def marcar_notificacion_leida(request, notificacion_id):
    """Marcar una notificación como leída"""
    from apps.notifications.models import Notification
    
    notificacion = get_object_or_404(Notification, id=notificacion_id, usuario=request.user)
    notificacion.leido = True
    notificacion.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('dashboard_notificaciones')


@login_required
@user_passes_test(is_staff_user)
@require_http_methods(['POST'])
def eliminar_notificacion(request, notificacion_id):
    """Eliminar una notificación"""
    from apps.notifications.models import Notification
    
    notificacion = get_object_or_404(Notification, id=notificacion_id, usuario=request.user)
    notificacion.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, 'Notificación eliminada exitosamente.')
    return redirect('dashboard_notificaciones')


@login_required
@user_passes_test(is_staff_user)
@require_http_methods(['POST'])
def marcar_todas_leidas(request):
    """Marcar todas las notificaciones como leídas"""
    from apps.notifications.models import Notification
    
    count = Notification.objects.filter(usuario=request.user, leido=False).update(leido=True)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'count': count})
    
    messages.success(request, f'{count} notificaciones marcadas como leídas.')
    return redirect('dashboard_notificaciones')

@login_required
def api_get_calendar_events(request):
    
    # 1. ID DEL CALENDARIO
    CALENDAR_ID = '7505ae36af692d9dc952769cb67cb09e5624f1c041e7e99c0c7efb2928b345b0@group.calendar.google.com' 

    # 2. RUTA A CREDENCIALES
    CREDENTIALS_FILE = settings.BASE_DIR / 'google-credentials.json'

    # 3. PERMISOS
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

    print(f"[DEBUG] Intentando cargar calendario: {CALENDAR_ID}")
    print(f"[DEBUG] Buscando credenciales en: {CREDENTIALS_FILE}")

    try:
        # Carga las credenciales del archivo JSON
        creds = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=SCOPES)
        print("[DEBUG] Credenciales cargadas exitosamente.")

        # Construye el servicio de la API
        service = build('calendar', 'v3', credentials=creds)
        print("[DEBUG] Servicio de API de Google construido.")

        # Llama a la API
        now = datetime.now(dt_timezone.utc).isoformat()  # 'Z' indica UTC
        
        events_result = service.events().list(
            calendarId=CALENDAR_ID, 
            timeMin=now,
            maxResults=50,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        print("[DEBUG] Llamada a la API de Google exitosa.")
        events = events_result.get('items', [])
        print(f"[DEBUG] Encontrados {len(events)} eventos.")

        # FORMATEA LOS EVENTOS PARA FULLCALENDAR
        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            formatted_events.append({
                'title': event.get('summary', 'Evento sin título'),
                'start': start,
                'end': end,
                'id': event['id'],
            })

        return JsonResponse(formatted_events, safe=False)

    except Exception as e:
        # --- ESTA ES LA PARTE IMPORTANTE ---
        # ¡Imprime el error completo en tu terminal de Django!
        print("="*50)
        print("¡ERROR! Falló la API de Google Calendar:")
        traceback.print_exc() # Esto imprimirá el error rojo
        print("="*50)
        # -----------------------------------
        return JsonResponse({'error': str(e)}, status=500)

