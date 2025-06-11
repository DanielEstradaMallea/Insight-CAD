from django.urls import path
from . import views
from .views import ValidarRUTView

app_name = 'persona'

urlpatterns = [
    #Personas
    path('personas/', views.PersonaListView.as_view(), name='list'),
    path('agregar_persona/', views.PersonaCreateView.as_view(), name='create'),
    path('editar_persona/<int:pk>/', views.PersonaUpdateView.as_view(), name='update'),
    path('eliminar_persona/<int:pk>/', views.PersonaDeleteView.as_view(), name='delete'),
    # Tipos de Personas
    path('tipos_personas/', views.listar_tipos_personas, name='listar_tipos_personas'),
    path('editar_tipo_persona/', views.editar_tipo_persona, name='editar_tipo_persona'),
    path('agregar_tipo_persona/', views.agregar_tipo_persona, name='agregar_tipo_persona'),
    path('validar-run/', ValidarRUTView.as_view(), name='validar_run_ajax'),  # URL para la validación AJAX
    path('personas/buscar/', views.buscar_personas, name='buscar_personas'),
    path('tipos-personas/json/', views.listar_tipos_personas_json, name='tipos_personas_json'),
    path('lista-gris/', views.lista_gris_view, name='lista_gris_persona'),

]