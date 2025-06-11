from django.urls import path
from apps.mantenedores import views

app_name = 'mantenedor'

urlpatterns = [
    path('estados-civiles/', views.listar_estados_civiles, name='listar_estados_civiles'),
    path('editar_estado/', views.editar_estado, name='editar_estado'),
    path('agregar_estado/', views.agregar_estado, name='agregar_estado'),
    path('generos/', views.listar_genero, name='listar_genero'),
    path('editar_genero/', views.editar_genero, name='editar_genero'),
    path('agregar_genero/', views.agregar_genero, name='agregar_genero')
]
