from django.urls import path
from . import views

app_name = 'mapa' 

urlpatterns = [
    path('eventos/', views.obtener_eventos, name='obtener_eventos'),  # Ruta para la API
    path('eventos_calor/', views.mapa_calor_eventos, name='obtener_eventos_calor'),  # Ruta para la API
    path('', views.mostrar_mapa, name='mostrar_mapa'),  # Ruta para la vista del mapa
    path('mapagps/', views.mostrar_mapa_gps, name='mostrar_mapa_gps'),  # Ruta para la vista del mapa gps
    path('mapa-calor/', views.mostrar_mapa_calor, name='mostrar_mapa_calor'),  # Ruta para la vista del mapa gps
    path('infoscan-eventos/',views.infoscan_eventos,name='infoscan_eventos'), #ruta api infoscan eventos
    path('infoscan/',views.infoscan_mapa,name='infoscan'),
    path('mapa-eventos/', views.mapa_eventos, name='mapa_eventos'),
    path('api/eventos/', views.api_eventos, name='api_eventos'),
    path('export-cluster-excel/', views.export_cluster_excel, name='export_cluster_excel'),
    path('dashboard/', views.dashboard_view, name='dashboard'),  # Vista HTML
    path('dashboard/data/', views.dashboard_eventos_data, name='dashboard_data'),
]
