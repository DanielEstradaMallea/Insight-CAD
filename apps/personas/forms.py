from django import forms
from .models import PerPersonas
from .validators import validar_rut
from apps.mantenedores.models import AdmComunas, AdmPaises, AdmGenero, AdmEstadosCiviles

class PersonaForm(forms.ModelForm):
    class Meta:
        model = PerPersonas
        fields = '__all__'
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rut'].validators.append(validar_rut)

        # Excluir campos que no deben mostrarse en el formulario
        self.fields.pop('id_usuario', None)
        self.fields.pop('fecha_registro', None)
        self.fields['lista_gris'].initial = 'NO'
        self.fields.pop('lista_gris', None)

    # Personalizar cómo se muestran las opciones en campos relacionados
        self.fields['id_pais'].label_from_instance = lambda obj: obj.nombre
        self.fields['id_comuna'].label_from_instance = lambda obj: obj.nombre
        self.fields['id_genero'].label_from_instance = lambda obj: obj.nombre
        self.fields['id_estado_civil'].label_from_instance = lambda obj: obj.nombre

        # Inicializar el queryset de id_comuna con todas las comunas
        self.fields['id_pais'].queryset = AdmPaises.objects.all()
        self.fields['id_comuna'].queryset = AdmComunas.objects.all()
        self.fields['id_genero'].queryset = AdmGenero.objects.filter(activo='SI')
        self.fields['id_estado_civil'].queryset = AdmEstadosCiviles.objects.filter(activo='SI')

    # ---- AQUI AGREGAS LAS CLASES BOOTSTRAP ----
        for name, field in self.fields.items():
            if field.widget.__class__.__name__ in ['Select', 'SelectMultiple']:
                field.widget.attrs['class'] = 'form-select form-select-sm'
            elif field.widget.__class__.__name__ == 'CheckboxInput':
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control form-control-sm'