from django.http import HttpResponse

def index(request):
    return HttpResponse('Главная страница моего блога')

def group_posts(request, slug):
    return HttpResponse('На этой странице будут посты, отфильтрованные по группам')
# Create your views here.
