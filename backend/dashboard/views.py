from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib import messages
from datetime import datetime, timedelta
from apps.users.models import User
from apps.blog.models import Categoria, Articulo
from apps.radio.models import Programa, EstacionRadio, HorarioPrograma
from apps.chat.models import ChatMessage
from apps.contact.models import Contacto, Suscripcion, Estado
from apps.emergente.models import BandaEmergente 


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
def dashboard_blog(request):
    """Gestión del blog"""
    posts = Articulo.objects.all().order_by('-fecha_creacion')
    return render(request, 'dashboard/blog.html', {'posts': posts})

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

# CRUD Operations for Blog Posts
@login_required
@user_passes_test(is_staff_user)
def create_post(request):
    """Crear nuevo artículo del blog"""
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        contenido = request.POST.get('contenido')
        resumen = request.POST.get('resumen')
        categoria = request.POST.get('categoria')
        tags = request.POST.get('tags')
        publicado = request.POST.get('publicado') == 'on'
        imagen_url = request.POST.get('imagen_url')
        
        try:
            # Obtener la categoría por ID
            categoria_obj = Categoria.objects.get(id=categoria) if categoria else None
            
            post = Articulo.objects.create(
                titulo=titulo,
                contenido=contenido,
                resumen=resumen,
                categoria=categoria_obj,
                publicado=publicado,
                imagen_url=imagen_url,
                autor=request.user
            )
            messages.success(request, f'Artículo "{titulo}" creado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al crear artículo: {str(e)}')
    
    return redirect('dashboard_blog')

@login_required
@user_passes_test(is_staff_user)
def edit_post(request, post_id):
    """Editar artículo del blog"""
    post = get_object_or_404(BlogPost, id=post_id)
    
    if request.method == 'POST':
        post.titulo = request.POST.get('titulo')
        post.contenido = request.POST.get('contenido')
        post.resumen = request.POST.get('resumen')
        post.categoria = request.POST.get('categoria')
        post.tags = request.POST.get('tags')
        post.publicado = request.POST.get('publicado') == 'on'
        post.imagen_url = request.POST.get('imagen_url')
        
        try:
            post.save()
            messages.success(request, f'Artículo "{post.titulo}" actualizado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al actualizar artículo: {str(e)}')
    
    return redirect('dashboard_blog')

@login_required
@user_passes_test(is_staff_user)
def delete_post(request, post_id):
    """Eliminar artículo del blog"""
    post = get_object_or_404(BlogPost, id=post_id)
    
    if request.method == 'POST':
        titulo = post.titulo
        try:
            post.delete()
            messages.success(request, f'Artículo "{titulo}" eliminado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar artículo: {str(e)}')
    
    return redirect('dashboard_blog')

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
    news = get_object_or_404(News, id=news_id)
    
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
def dashboard_emergentes(request):
    """Gestión de bandas emergentes"""
    bandas = BandaEmergente.objects.select_related(
        'estado', 'genero', 'usuario', 'comuna__ciudad__pais'
    ).prefetch_related('integrantes', 'links').order_by('-fecha_envio')
    
    # Obtener todos los estados disponibles para bandas
    estados_disponibles = Estado.objects.filter(tipo_entidad='banda').order_by('nombre')
    
    # Estadísticas por estado
    stats_estados = {}
    for estado in estados_disponibles:
        count = bandas.filter(estado=estado).count()
        stats_estados[estado.nombre] = count
    
    context = {
        'bandas': bandas,
        'estados_disponibles': estados_disponibles,
        'stats_estados': stats_estados,
        'total_bandas': bandas.count()
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
def delete_banda(request, banda_id):
    """Eliminar una banda emergente"""
    banda = get_object_or_404(BandaEmergente, id=banda_id)
    if request.method == 'POST':
        nombre = banda.nombre_banda
        try:
            banda.delete()
            messages.success(request, f"Banda '{nombre}' eliminada exitosamente.")
        except Exception as e:
            messages.error(request, f"Error al eliminar banda: {str(e)}")
    return redirect('dashboard_emergentes')


@login_required
@user_passes_test(is_staff_user)
def view_banda(request, banda_id):
    """Ver detalle completo de una banda emergente"""
    banda = get_object_or_404(BandaEmergente, id=banda_id)
    return render(request, 'dashboard/emergente_detail.html', {'banda': banda})
