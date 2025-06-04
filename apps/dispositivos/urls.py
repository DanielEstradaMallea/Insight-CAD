from django.urls import path
from . import views

app_name = 'dispositivo'

urlpatterns = [
    # Tipos de Dispositivos
    path('tipos_dispositivos/', views.listar_tipos_dispositivos, name='listar_tipos_dispositivos'),
    path('editar_tipo_dispositivo/', views.editar_tipo_dispositivo, name='editar_tipo_dispositivo'),
    path('agregar_tipo_dispositivo/', views.agregar_tipo_dispositivo, name='agregar_tipo_dispositivo'),
    # Tipos de Sensores
    path('tipos_sensores/', views.listar_tipos_sensores, name='listar_tipos_sensores'),
    path('editar_tipo_sensor/', views.editar_tipo_sensor, name='editar_tipo_sensor'),
    path('agregar_tipo_sensor/', views.agregar_tipo_sensor, name='agregar_tipo_sensor'),
    # Compañías SIM
    path('companias_sim/', views.listar_companias_sim, name='listar_companias_sim'),
    path('editar_compania_sim/', views.editar_compania_sim, name='editar_compania_sim'),
    path('agregar_compania_sim/', views.agregar_compania_sim, name='agregar_compania_sim'),
     # Tipos de SIM
    path('tipos_sim/', views.listar_tipos_sim, name='listar_tipos_sim'),
    path('editar_tipo_sim/', views.editar_tipo_sim, name='editar_tipo_sim'),
    path('agregar_tipo_sim/', views.agregar_tipo_sim, name='agregar_tipo_sim'),
    #Gestion de dispositivos
    path('listar/', views.listar_dispositivos, name='listar_dispositivos'),
    path('agregar_dispositivo/', views.agregar_dispositivo, name='agregar_dispositivo'),
    path('editar_dispositivo/<int:id_dispositivo>/', views.editar_dispositivo, name='editar_dispositivo'),
]