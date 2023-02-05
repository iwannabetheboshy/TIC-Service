from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.user_login, name='login'),
    path('ce', views.index, name='ce'),
    path('caf', views.caf, name='caf'),
    path('tour', views.tour, name='tour'),
    path('culture', views.culture, name='culture'),
    path('attr', views.attr, name='attr'),
    path('search', views.search, name='search'),
    path('download_file', views.download_file, name='download_file'),
]
