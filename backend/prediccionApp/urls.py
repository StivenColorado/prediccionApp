from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Vista por defecto
    path('encuestas/', views.obtener_encuestas, name='obtener_encuestas'),
]
