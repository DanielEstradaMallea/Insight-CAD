from django.urls import path
from . import views

app_name = 'vehiculos'


urlpatterns = [
    path('vehiculos/', views.vehiculos_list, name='listar_vehiculos'),
    path('agregar/', views.agregar_vehiculo, name='agregar_vehiculo'),
    path('modificar/<int:id_vehiculo>/', views.modificar_vehiculo, name='modificar_vehiculo'),
    #Tipos
    path('tipos-vehiculos/', views.listar_tipos_vehiculos, name='listar_tipos_vehiculos'),    
    path('editar-tipo-vehiculo/', views.editar_tipo_vehiculo, name='editar_tipo_vehiculo'),    
    path('agregar-tipo-vehiculo/', views.agregar_tipo_vehiculo, name='agregar_tipo_vehiculo'),
    #Marcas
    path('marcas_vehiculos/', views.listar_marcas_vehiculos, name='listar_marcas_vehiculos'),
    path('editar_marca_vehiculo/', views.editar_marca_vehiculo, name='editar_marca_vehiculo'),
    path('agregar_marca_vehiculo/', views.agregar_marca_vehiculo, name='agregar_marca_vehiculo'),
    #busqueda ajax
    path('api/buscar-vehiculos/',views.buscar_vehiculos, name='buscar_vehiculos'),
    # Listar todas las asignaciones
    path('api/asignaciones/', views.get_asignaciones, name='get_asignaciones'),
    # Obtener la asignación de un evento específico
    path('api/asignaciones/<int:evento_id>/', views.get_asignacion, name='get_asignacion'),
    # Endpoint para asignar una cuadrilla a un evento
    path('api/asignar_cuadrilla/', views.asignar_cuadrilla, name='asignar_cuadrilla'),
    # Endpoint para cancelar la asistencia
    path('api/cancelar_asistencia/', views.cancelar_asistencia, name='cancelar_asistencia'),
    
]