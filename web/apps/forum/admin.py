from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import News, NewsComment, Category, Thread, ThreadPost, Reaction

# Новости
class NewsAdmin(SummernoteModelAdmin):
    summernote_fields = ('content',)
    list_display = ('title', 'author', 'created_at')

# Категории (Разделы форума)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_admin_only', 'is_feedback')
    list_editable = ('is_admin_only', 'is_feedback') # Можно менять галочки прямо в списке

# Темы и посты
class ThreadAdmin(SummernoteModelAdmin):
    summernote_fields = ('content',)
    list_display = ('title', 'category', 'author', 'created_at', 'is_closed')
    list_filter = ('category', 'is_closed')

class ThreadPostAdmin(SummernoteModelAdmin):
    summernote_fields = ('content',)
    list_display = ('thread', 'author', 'created_at')

# Регистрируем всё
admin.site.register(News, NewsAdmin)
admin.site.register(NewsComment)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(ThreadPost, ThreadPostAdmin)
admin.site.register(Reaction)