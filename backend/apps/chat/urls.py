from django.urls import path
from django.http import JsonResponse
from . import views

def chat_info(request):
    return JsonResponse({
        'message': 'Chat API',
        'endpoints': {
            'messages': '/api/chat/messages/',
            'messages_by_room': '/api/chat/messages/{room}/',
            'delete_message': '/api/chat/messages/{id}/delete/',
            'radio_status': '/api/chat/radio-status/'
        }
    })

urlpatterns = [
    path('', chat_info, name='chat-info'),
    path('messages/', views.ChatMessageListView.as_view(), name='chat-messages'),
    path('messages/<str:sala>/', views.ChatMessageListView.as_view(), name='chat-messages-sala'),
    path('messages/<int:pk>/delete/', views.ChatMessageDeleteView.as_view(), name='chat-message-delete'),
    path('messages/clear/', views.clear_all_messages, name='chat-clear-all'),
    path('users/<int:user_id>/toggle-block/', views.toggle_user_block, name='chat-toggle-user-block'),
    path('radio-status/', views.RadioStatusView.as_view(), name='radio-status'),
]
