from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('news/create/', views.create_news, name='create_news'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),

    path('forum/', views.forum_index, name='forum_index'),
    path('forum/cat/<int:pk>/', views.category_detail, name='category_detail'),
    path('forum/cat/<int:pk>/create/', views.create_thread, name='create_thread'),
    path('forum/thread/<int:pk>/', views.thread_detail, name='thread_detail'),

    path('chat/get/', views.chat_get_messages, name='chat_get'),
    path('chat/send/', views.chat_send_message, name='chat_send'),

    path('rules/', views.rules, name='rules'),

    path('reaction/<str:model_type>/<int:pk>/<str:value>/', views.add_reaction, name='add_reaction'),
]