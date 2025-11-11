from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
import os

@csrf_exempt
@require_http_methods(["GET"])
def api_publicidad_media(request, campania_id):
    """API para obtener la información de medios de una campaña de publicidad
    
    Devuelve los detalles de una campaña específica incluyendo sus ítems e imágenes asociadas.
    """
    try:
        from apps.publicidad.models import CampaniaPublicidadWeb, ItemSolicitudWeb
        
        # Obtener la campaña específica
        campania = CampaniaPublicidadWeb.objects.get(id=campania_id)
        
        # Obtener los ítems de la campaña con sus imágenes
        items = campania.items_web.all()
        items_data = []
        
        for item in items:
            imagenes = [{
                'id': img.id,
                'imagen': request.build_absolute_uri(img.imagen.url) if item.imagen else None,
                'descripcion': img.descripcion,
                'orden': img.orden,
                'fecha_subida': img.fecha_subida.strftime('%Y-%m-%d %H:%M:%S') if img.fecha_subida else None
            } for img in item.imagenes_web.all()]
            
            items_data.append({
                'id': item.id,
                'ubicacion_id': item.ubicacion_id,
                'imagenes': imagenes
            })
        
        return JsonResponse({
            'success': True,
            'campania': {
                'id': campania.id,
                'nombre': campania.nombre,
                'fecha_inicio': campania.fecha_inicio.strftime('%Y-%m-%d') if campania.fecha_inicio else None,
                'fecha_fin': campania.fecha_fin.strftime('%Y-%m-%d') if campania.fecha_fin else None,
                'estado': campania.estado,
                'items': items_data
            }
        })
    except CampaniaPublicidadWeb.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Campaña no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
