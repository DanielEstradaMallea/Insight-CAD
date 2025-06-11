from django import forms
from .models import VehVehiculos

class VehVehiculoForm(forms.ModelForm):
    class Meta:
        model = VehVehiculos
        fields = ['patente', 'id_marca_vehiculo', 'modelo', 'color', 'id_tipo_vehiculo', 'lista_gris', 'activo', 'id_usuario']
