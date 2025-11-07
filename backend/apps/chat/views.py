from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import ChatMessage
from .serializers import ChatMessageSerializer
from apps.radio.models import EstacionRadio

class ChatMessageListView(generics.ListCreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]

    def get_queryset(self):
        sala = self.kwargs.get('sala', 'radio-oriente')
        return ChatMessage.objects.filter(
            sala=sala
        ).order_by('-fecha_envio')[:50]

    def perform_create(self, serializer):
        # Verificar si el usuario está bloqueado
        if self.request.user.chat_bloqueado:
            raise ValidationError({'detail': 'Has sido bloqueado del chat. Contacta con un administrador.'})

        # Verificar si la radio está online
        try:
            radio = EstacionRadio.objects.first()
            if not radio or not radio.activo:
                raise ValidationError({'detail': 'El chat solo está disponible cuando la radio está en vivo'})
        except EstacionRadio.DoesNotExist:
            raise ValidationError({'detail': 'No se pudo verificar el estado de la radio'})

        sala = self.kwargs.get('sala', 'radio-oriente')
        serializer.save(
            id_usuario=self.request.user.id,
            usuario_nombre=self.request.user.username,
            sala=sala,
            tipo='user'
        )

class ChatMessageDeleteView(generics.DestroyAPIView):
    """Vista para que los administradores eliminen mensajes del chat"""
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAdminUser]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    queryset = ChatMessage.objects.all()

class RadioStatusView(APIView):
    """Vista para verificar si la radio está online"""
    permission_classes = []

    def get(self, request):
        try:
            radio = EstacionRadio.objects.first()
            return Response({
                'is_online': radio.activo if radio else False,
                'listeners_count': radio.listeners_count if radio else 0
            })
        except EstacionRadio.DoesNotExist:
            return Response({
                'is_online': False,
                'listeners_count': 0
            })

@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAdminUser])
def toggle_user_block(request, user_id):
    """Bloquear o desbloquear usuario del chat"""
    try:
        User = settings.AUTH_USER_MODEL
        from django.apps import apps
        UserModel = apps.get_model(User)
        user = get_object_or_404(UserModel, id=user_id)

        user.chat_bloqueado = not user.chat_bloqueado
        user.save()

        return Response({
            'success': True,
            'bloqueado': user.chat_bloqueado,
            'message': f'Usuario {"bloqueado" if user.chat_bloqueado else "desbloqueado"} correctamente'
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAdminUser])
def clear_all_messages(request):
    """Limpiar todos los mensajes del chat"""
    try:
        sala = request.data.get('sala', 'radio-oriente')
        deleted_count = ChatMessage.objects.filter(sala=sala).delete()[0]

        return Response({
            'success': True,
            'deleted_count': deleted_count,
            'message': f'Se eliminaron {deleted_count} mensajes correctamente'
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
