from django.urls import path
from apps.eventos import views
from .views import EventoCreateView

app_name = 'evento'

urlpatterns = [
    path('reporte/', views.reporte_eventos, name='reporte_eventos'),
    path('tipos-eventos/', views.cargar_tipos_eventos, name='cargar_tipos_eventos'),
    path('cargar_subtipos_eventos/', views.cargar_subtipos_eventos, name='cargar_subtipos_eventos'),
    path('eventos-filtrados/', views.obtener_eventos_filtrados, name='obtener_eventos_filtrados'),
    path('tipos/', views.listar_tipo_evento, name='listar_tipo'),
    path('subtipos/',views.mostrar_subtipo_evento, name='mostrar_evento'),
    path('editar_tipo/', views.editar_tipo_evento, name='editar_tipo'),
    path('agregar_tipo/', views.agregar_tipo_evento, name='agregar_tipo'),
    path('obtener-imagenes-evento/<int:evento_id>/', views.obtener_imagenes_evento, name='obtener_imagenes_evento'),
    # Procedencias
    path('procedencias/', views.listar_procedencias, name='listar_procedencias'),
    path('editar_procedencia/', views.editar_procedencia, name='editar_procedencia'),
    path('agregar_procedencia/', views.agregar_procedencia, name='agregar_procedencia'),
     # Estados
    path('estados/', views.listar_estados, name='listar_estados_evento'),
    path('editar_estado-evento/', views.editar_estado, name='editar_estado_evento'),
    path('agregar_estado-evento/', views.agregar_estado, name='agregar_estado_evento'),
    #Formulario Evento
    path('nuevo_evento/', EventoCreateView.as_view(), name='nuevo_evento'),
    #SubTipo
    path('agregar_subtipo/', views.agregar_subtipo, name='agregar_subtipo'), 
    path('api/subtipos/', views.get_subtipos, name='get_subtipos'),
    path('editar_subtipo/', views.editar_subtipo, name='editar_subtipo'),
    path('eliminar_subtipo/', views.eliminar_subtipo, name='eliminar_subtipo'),
   # urls.py
    path('obtener-detalle-evento/<int:evento_id>/', views.obtener_detalle_evento, name='detalle-evento'),
    #btn alerta eventos
    path('cambiar-estado-alerta/<int:evento_id>/', views.cambiar_estado_alerta, name='cambiar-estado-alerta'),
    # Tabla eventos-antecedentes
    path('obtener-antecedentes/<int:evento_id>/', views.obtener_antecedentes, name='obtener-antecedentes'),
    path('guardar-antecedente/<int:evento_id>/', views.guardar_antecedente, name='guardar-antecedente'),
    # Tabla Eventos-Estado
    path('obtener-estados/', views.obtener_estados, name='obtener-estados'),
    path('cambiar-estado-evento/<int:evento_id>/', views.cambiar_estado_evento, name='cambiar-estado-evento'),
    path('obtener-historial-estados/<int:evento_id>/', views.obtener_historial_estados, name='obtener-historial-estados'),

    
    
]