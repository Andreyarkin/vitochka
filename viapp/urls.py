# адреса для страниц приложения viapp

from django.urls import path

from . import views

app_name = 'viapp'
urlpatterns = [
    #Homepage
    path('',views.index, name = 'index'),
]