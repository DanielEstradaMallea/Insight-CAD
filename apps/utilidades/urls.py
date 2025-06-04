from django.urls import path
from . import views

app_name = 'utilidades'


urlpatterns = [
    path('registrar-persona/', views.registrar_persona_evento, name='registrar_persona_evento'),
    path('api/obtener_personas_evento/', views.obtener_personas_evento, name='obtener_personas_evento'),
    path('registrar-vehiculo/', views.registrar_vehiculo_evento, name='registrar_vehiculo_evento'),
    path('obtener-vehiculos-evento/', views.obtener_vehiculos_evento, name='obtener_vehiculos_evento'),
    path('buscar-persona/', views.buscar_persona, name='buscar_persona'),
    path('eventos-persona/', views.eventos_persona, name='eventos_persona'),
    path('export-eventos-excel/', views.export_eventos_excel, name='export_eventos_excel'),
    path('buscar-vehiculo/', views.buscar_vehiculo, name='buscar_vehiculo'),
    path('eventos-vehiculo/', views.eventos_vehiculo, name='eventos_vehiculo'),
    path('export-vehiculos-excel/', views.export_vehiculos_excel, name='export_vehiculos_excel'),
]