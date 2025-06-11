from django.urls import path
from .views import (EmpresaListView, EmpresaCreateView, EmpresaUpdateView, EmpresaDeleteView,
                    ValidarRUTView)
from apps.empresas import views



app_name = 'empresa'

urlpatterns = [
    path('empresas', EmpresaListView.as_view(), name='list-empresas'),
    path('agregar-empresa/', EmpresaCreateView.as_view(), name='add-empresa'),
    path('editar-empresa/<int:pk>/', EmpresaUpdateView.as_view(), name='edit-empresa'),
    path('eliminar-empresa/<int:pk>/', EmpresaDeleteView.as_view(), name='delete-empresa'),
    path('validar-rut/', ValidarRUTView.as_view(), name='validar_rut_ajax'),  # URL para la validación AJAX
    path('cargar-sucursales/', views.cargar_sucursales, name='cargar_sucursales'),
     # Gestión de Sucursales
    path('empresas/<int:empresa_id>/sucursales/', views.listar_sucursales, name='list-sucursales'),
    path('empresas/<int:empresa_id>/sucursales/add/', views.crear_sucursal, name='add-sucursal'),
    path('sucursales/<int:id>/edit/', views.actualizar_sucursal, name='editar-sucursal'),
    path('sucursales/<int:id>/delete/', views.eliminar_sucursal, name='eliminar-sucursal'),
    path('cargar-sucursal/<int:id_sucursal>/', views.cargar_sucursal, name='cargar-sucursal'),
    path('obtener-redes-apoyo/<int:id_sucursal>/', views.obtener_redes_apoyo, name='obtener_redes_apoyo'),
    path('guardar-red-apoyo/<int:id_sucursal>/', views.guardar_red_apoyo, name='guardar_red_apoyo'),
    path('eliminar-red-apoyo/<int:id_nr>/', views.eliminar_red_apoyo, name='eliminar_red_apoyo'),
    
   
]