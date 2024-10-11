from django.urls import path
from .views import index, obtener_encuestas, predecir_recomendacion

urlpatterns = [
    path('', index, name='index'),
    path('encuestas/', obtener_encuestas, name='obtener_encuestas'),
    path('predecir/', predecir_recomendacion, name='predecir_recomendacion'),
]
