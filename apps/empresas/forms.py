from django import forms
from .models import EmpEmpresas, EmpSucursales
from .validators import validar_rut

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = EmpEmpresas
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_representante': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_representante': forms.TextInput(attrs={'class': 'form-control'}),
            'email_representante': forms.EmailInput(attrs={'class': 'form-control'}),
            'activo': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Validador RUT
        self.fields['rut'].validators.append(validar_rut)

        # Excluir campos no editables
        self.fields.pop('id_usuario', None)
        self.fields.pop('fecha_registro', None)

        # Estado SI/NO como select con Bootstrap
        self.fields['activo'].choices = [('SI', 'Sí'), ('NO', 'No')]
        self.fields['activo'].widget = forms.Select(attrs={'class': 'form-select'})

class SucursalForm(forms.ModelForm):
    class Meta:
        model = EmpSucursales
        fields = ['nombre', 'direccion', 'latitud', 'longitud', 'id_comuna']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'latitud': forms.TextInput(attrs={'class': 'form-control'}),
            'longitud': forms.TextInput(attrs={'class': 'form-control'}),
            'id_comuna': forms.Select(attrs={'class': 'form-select'}),
        }
