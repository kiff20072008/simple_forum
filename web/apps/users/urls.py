from django.urls import path
from . import views

urlpatterns = [
    path('', views.register, name='register'),
    path('staff/', views.staff_users_list, name='staff_users_list'),
    path('staff/ban/<int:user_id>/', views.toggle_ban, name='toggle_ban'),
]