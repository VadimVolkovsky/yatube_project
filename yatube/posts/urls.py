# posts/urls.py

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path('group/<slug:slug>/', views.group_posts),
    ]
