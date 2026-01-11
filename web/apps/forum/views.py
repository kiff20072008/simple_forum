from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from .models import News, NewsComment, Category, Thread, ThreadPost, Reaction, ChatMessage
from .forms import NewsForm, NewsCommentForm, ThreadForm, PostForm
from django.http import JsonResponse
import json


# Хелперы прав доступа
def can_create_news(user):
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name='Moderators').exists())


def can_interact(user):
    return user.is_authenticated and not user.is_banned


# === ГЛАВНАЯ (НОВОСТИ) ===
def home(request):
    news_list = News.objects.all().order_by('-created_at')
    return render(request, 'home.html', {'news_list': news_list, 'can_create_news': can_create_news(request.user)})


@login_required
def create_news(request):
    if not can_create_news(request.user):
        raise PermissionDenied
    if request.method == 'POST':
        form = NewsForm(request.POST)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user
            news.save()
            return redirect('home')
    else:
        form = NewsForm()
    return render(request, 'forum/create_news.html', {'form': form})


def news_detail(request, pk):
    news = get_object_or_404(News, pk=pk)
    form = NewsCommentForm()

    if request.method == 'POST':
        if not can_interact(request.user):
            return HttpResponseForbidden("Вы забанены или не авторизованы")
        form = NewsCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.news = news
            comment.author = request.user
            comment.save()
            return redirect('news_detail', pk=pk)

    return render(request, 'forum/news_detail.html',
                  {'news': news, 'form': form, 'can_interact': can_interact(request.user)})


# === ФОРУМ ===
def forum_index(request):
    admin_categories = Category.objects.filter(is_admin_only=True)
    general_categories = Category.objects.filter(is_admin_only=False)

    context = {
        'admin_categories': admin_categories,
        'general_categories': general_categories
    }
    return render(request, 'forum/index.html', context)


def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    threads = category.threads.all().order_by('-created_at')

    # Логика прав на создание темы
    can_post = False
    if request.user.is_authenticated and not request.user.is_banned:
        if category.is_admin_only:
            # Если раздел админский
            if category.is_feedback:
                can_post = True  # В "Связь с адм" могут писать все
            elif request.user.is_superuser or request.user.groups.filter(name='Moderators').exists():
                can_post = True  # Иначе только модеры
        else:
            can_post = True  # Обычный раздел

    return render(request, 'forum/category_detail.html',
                  {'category': category, 'threads': threads, 'can_post': can_post})


@login_required
def create_thread(request, pk):
    category = get_object_or_404(Category, pk=pk)

    # Проверка прав (дубль логики для безопасности)
    allowed = False
    if not request.user.is_banned:
        if category.is_admin_only:
            if category.is_feedback or request.user.is_superuser or request.user.groups.filter(
                    name='Moderators').exists():
                allowed = True
        else:
            allowed = True

    if not allowed:
        raise PermissionDenied

    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.category = category
            thread.author = request.user
            thread.save()
            return redirect('category_detail', pk=pk)
    else:
        form = ThreadForm()
    return render(request, 'forum/create_thread.html', {'form': form, 'category': category})


def thread_detail(request, pk):
    thread = get_object_or_404(Thread, pk=pk)
    posts = thread.posts.all()
    form = PostForm()

    # Логика прав комментирования
    can_reply = False
    if request.user.is_authenticated and not request.user.is_banned:
        if thread.category.is_admin_only:
            if thread.category.is_feedback:
                # В своей теме связи с администрацией пользователь может отвечать, в чужих - нет (для приватности можно допилить, но пока упростим: писать могут все)
                can_reply = True
            elif request.user.is_superuser or request.user.groups.filter(name='Moderators').exists():
                can_reply = True
        else:
            can_reply = True

    if request.method == 'POST':
        if not can_reply:
            return HttpResponseForbidden()
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.thread = thread
            post.author = request.user
            post.save()
            return redirect('thread_detail', pk=pk)

    return render(request, 'forum/thread_detail.html',
                  {'thread': thread, 'posts': posts, 'form': form, 'can_reply': can_reply})


# === РЕАКЦИИ ===
@login_required
def add_reaction(request, model_type, pk, value):
    value = int(value)

    if request.user.is_banned:
        return HttpResponseForbidden()

    # Определение модели по строке
    model_map = {
        'news': News,
        'news_comment': NewsComment,
        'thread': Thread,
        'post': ThreadPost
    }
    model = model_map.get(model_type)
    if not model:
        return HttpResponseForbidden()

    obj = get_object_or_404(model, pk=pk)
    ct = ContentType.objects.get_for_model(obj)

    # Удалить старую реакцию если есть, или обновить
    reaction, created = Reaction.objects.get_or_create(
        user=request.user,
        content_type=ct,
        object_id=obj.id,
        defaults={'value': value}
    )
    if not created:
        if reaction.value == value:
            reaction.delete()  # Тоггл (убрать лайк)
        else:
            reaction.value = value
            reaction.save()

    return redirect(request.META.get('HTTP_REFERER', '/'))


# === ЧАТ ===
def chat_get_messages(request):
    # Берем последние 50 сообщений
    messages = ChatMessage.objects.select_related('author').order_by('-created_at')[:50]
    results = []
    for msg in reversed(messages): # Разворачиваем, чтобы старые были сверху
        results.append({
            'author': msg.author.username,
            'avatar': msg.author.avatar.url if msg.author.avatar else None,
            'content': msg.content,
            'created_at': msg.created_at.strftime("%H:%M"),
            'is_me': request.user.is_authenticated and msg.author == request.user
        })
    return JsonResponse({'messages': results})

@login_required
def chat_send_message(request):
    if request.method == 'POST' and not request.user.is_banned:
        data = json.loads(request.body)
        content = data.get('message', '').strip()
        if content:
            ChatMessage.objects.create(author=request.user, content=content)
            return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

def rules(request):
    return render(request, 'forum/rules.html')