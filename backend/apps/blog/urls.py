from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from . import views

# Router para los ViewSets normalizados
router = DefaultRouter()
router.register(r'categorias', views.CategoriaViewSet)
router.register(r'articulos', views.ArticuloViewSet)

def blog_info(request):
    return JsonResponse({
        'message': 'Blog API',
        'endpoints': {
            'posts': '/api/blog/posts/',
            'post_detail': '/api/blog/posts/{id}/',
            'comments': '/api/blog/posts/{id}/comments/'
        }
    })

urlpatterns = [
    path('', blog_info, name='blog-info'),
    # APIs normalizadas
    path('api/', include(router.urls)),
    # APIs de compatibilidad para el frontend existente
    path('posts/', views.BlogPostListView.as_view(), name='blog-posts'),
    path('posts/<int:pk>/', views.BlogPostDetailView.as_view(), name='blog-post-detail'),
]
