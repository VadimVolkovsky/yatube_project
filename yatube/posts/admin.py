from django.contrib import admin
from .models import Post, Group


class PostAdmin(admin.ModelAdmin):
    # Поля, которые должны отображаться в админке сайта:
    list_display = (
    'pk',
    'text',
    'pub_date',
    'author',
    'group'
    )
    # функция фильтрации по дате:
    list_filter = ('pub_date',)
    # Выбор группы из списка:
    list_editable = ('group',)
    # интерфейс для поиска по тексту постов:
    search_fields = ('text',)
    # заглушка для всех колонок, где нет данных:
    empty_value_display = '-пусто-'
    
    # При регистрации модели Post источником 
    # конфигурации для неё назначаем класс PostAdmin
admin.site.register(Post, PostAdmin)

class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'description')
admin.site.register(Group, GroupAdmin)