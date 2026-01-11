from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import CustomUser
from django import forms

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'avatar')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# Управление пользователями для модераторов
def is_mod(user):
    return user.is_active and (user.is_superuser or user.groups.filter(name='Moderators').exists())

@user_passes_test(is_mod)
def staff_users_list(request):
    # Не показываем админов и модераторов в списке на бан, чтобы случайно не забанить своих
    users = CustomUser.objects.filter(is_superuser=False).exclude(groups__name='Moderators').order_by('-date_joined')
    return render(request, 'users/staff_list.html', {'users': users})

@user_passes_test(is_mod)
def toggle_ban(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if not user.is_superuser and not user.is_moderator():
        user.is_banned = not user.is_banned
        user.save()
    return redirect('staff_users_list')