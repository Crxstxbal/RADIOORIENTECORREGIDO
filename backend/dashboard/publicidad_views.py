from django.http import FileResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import os
import mimetypes

@csrf_exempt
@require_http_methods(["GET"])
def api_publicidad_media(request, campania_id):
    """
    Sirve directamente la imagen de una campaña de publicidad.
    Esta vista actúa como proxy para evitar bloqueos de AdBlockers.
    """
    try:
        from apps.publicidad.models import Publicidad, ItemSolicitudWeb
        import logging
        logger = logging.getLogger(__name__)

        # Obtener la campaña
        pub = get_object_or_404(Publicidad, id=campania_id)
        logger.info(f"[PUBLICIDAD MEDIA] Campaña ID: {campania_id}")

        # Obtener el archivo de media
        wc = getattr(pub, 'web_config', None)
        if not wc:
            logger.error(f"[PUBLICIDAD MEDIA] No se encontró web_config para campaña {campania_id}")
            return HttpResponse('No se encontró configuración web', status=404)

        archivo_media = getattr(wc, 'archivo_media', None)

        # Si no hay archivo_media, intentar obtener desde ItemSolicitudWeb
        if not archivo_media:
            logger.info(f"[PUBLICIDAD MEDIA] No hay archivo_media, buscando en ItemSolicitudWeb")
            try:
                import re
                desc = getattr(pub, 'descripcion', '') or ''
                m = re.search(r'Item\s*#(\d+)', desc)
                if m:
                    item_id = int(m.group(1))
                    item = ItemSolicitudWeb.objects.get(id=item_id)
                    img = item.imagenes_web.order_by('orden', 'fecha_subida').first()
                    if img and getattr(img, 'imagen', None):
                        archivo_media = img.imagen
                        logger.info(f"[PUBLICIDAD MEDIA] Imagen encontrada desde Item #{item_id}")
            except Exception as e:
                logger.error(f"[PUBLICIDAD MEDIA] Error al buscar imagen en Item: {str(e)}")

        if not archivo_media:
            logger.error(f"[PUBLICIDAD MEDIA] No se encontró imagen para campaña {campania_id}")
            return HttpResponse('No se encontró imagen', status=404)

        # Obtener la ruta del archivo
        try:
            file_path = archivo_media.path
            logger.info(f"[PUBLICIDAD MEDIA] Ruta del archivo: {file_path}")

            # Verificar que el archivo existe
            if not os.path.exists(file_path):
                logger.error(f"[PUBLICIDAD MEDIA] Archivo no encontrado en: {file_path}")
                return HttpResponse('Archivo no encontrado', status=404)

            # Detectar el tipo MIME
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                content_type = 'image/jpeg'  # Fallback a JPEG

            # Abrir y devolver el archivo
            response = FileResponse(open(file_path, 'rb'), content_type=content_type)

            # Headers para evitar bloqueos de AdBlockers
            response['Cache-Control'] = 'public, max-age=3600'
            response['Access-Control-Allow-Origin'] = '*'

            logger.info(f"[PUBLICIDAD MEDIA] Imagen servida correctamente: {file_path}")
            return response

        except Exception as e:
            logger.error(f"[PUBLICIDAD MEDIA] Error al acceder al archivo: {str(e)}")
            # Si falla al acceder al archivo, intentar con la URL
            try:
                media_url = getattr(archivo_media, 'url', None)
                if media_url:
                    logger.info(f"[PUBLICIDAD MEDIA] Redirigiendo a: {media_url}")
                    from django.http import HttpResponseRedirect
                    return HttpResponseRedirect(media_url)
            except Exception as e2:
                logger.error(f"[PUBLICIDAD MEDIA] Error al redirigir: {str(e2)}")
                pass

            return HttpResponse(f'Error al servir la imagen: {str(e)}', status=500)

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"[PUBLICIDAD MEDIA] Error general: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f'Error: {str(e)}', status=500)
