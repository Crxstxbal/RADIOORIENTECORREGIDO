from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def api_info(request):
    return JsonResponse({
        'message': 'Radio Oriente FM API',
        'version': '1.0',
        'endpoints': {
            'admin': '/admin/',
            'auth': '/api/auth/',
            'radio': '/api/radio/',
            'chat': '/api/chat/',
            'articulos': '/api/articulos/',
            'contact': '/api/contact/',
            'emergentes': '/api/emergentes/',
            'ubicacion': '/api/ubicacion/',
            'publicidad': '/api/publicidad/'
        }
    })

urlpatterns = [
    path('', api_info, name='api_info'),
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),
    path('api/auth/', include('apps.users.urls')),
    path('api/radio/', include('apps.radio.urls')),
    path('api/chat/', include('apps.chat.urls')),
    path('api/articulos/', include('apps.articulos.urls')),
    path('api/contact/', include('apps.contact.urls')),
    path('api/emergentes/', include('apps.emergente.urls')),
    path('api/ubicacion/', include('apps.ubicacion.urls')),
    path('api/publicidad/', include('apps.publicidad.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
