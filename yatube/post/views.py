
from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
# ice_cream/views.py



# Главная страница
def index(request):
    return HttpResponse('Главная страница')


# Страница со списком постов
def groups_posts(request):
    return HttpResponse('Список постов')

#Пост про мотоцикл
def post_detail(request, pk):
    return HttpResponse(f'CB400 Super Four Vtec2 {pk}') 

