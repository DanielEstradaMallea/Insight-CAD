from django import forms
from datetime import datetime
from .models import EveEventos, EveSubtipos, EveTipos, EveProcedencias, EveEstados, EveImagenesEventos
from apps.mantenedores.models import AdmComunas
from apps.empresas.models import EmpEmpresas, EmpSucursales

class EventoForm(forms.ModelForm):
    empresa = forms.ModelChoiceField(
        queryset=EmpEmpresas.objects.filter(activo='SI'),
        label="Empresa",
        required=False,
        widget=forms.Select(attrs={'id': 'id_empresa'})
    )
    id_sucursal = forms.ModelChoiceField(
        queryset=EmpSucursales.objects.none(),
        label="Sucursal",
        required=False,
        widget=forms.Select(attrs={'id': 'id_sucursal'})
    )

    class Meta:
        model = EveEventos
        fields = [
            'nombre', 'id_tipo', 'id_subtipo', 'id_procedencia',
            'fecha', 'hora', 'direccion', 'latitud', 'longitud',
            'id_comuna', 'id_estado_actual', 'alerta_encendida',
            'fecha_alerta', 'fecha_registro', 'detalle',
            'id_sucursal', 'empresa'
        ]
        widgets = {
            'fecha': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'max': datetime.now().date().strftime('%Y-%m-%d')
                }
            ),
            'hora': forms.TimeInput(attrs={'type': 'time'}),
            'fecha_alerta': forms.HiddenInput(),
            'alerta_encendida': forms.HiddenInput(),
            'fecha_registro': forms.HiddenInput(),
        }
        labels = {
            'id_estado_actual': 'Estado inicial del evento',
            'detalle': 'Descripción detallada del evento',
        }
        help_texts = {
            'latitud': 'Formato decimal (Ej: -33.456789)',
            'longitud': 'Formato decimal (Ej: -70.654321)',
        }

    def __init__(self, *args, tipo_evento_id=None, **kwargs):
        super().__init__(*args, **kwargs)

        # 1) Aplicar clases Bootstrap automáticamente
        for name, field in self.fields.items():
            widget = field.widget
            existing = widget.attrs.get('class', '').split()
            if isinstance(widget, (forms.Select, forms.NullBooleanSelect, forms.SelectMultiple)):
                existing.append('form-select')
            else:
                existing.append('form-control')
            widget.attrs['class'] = ' '.join(dict.fromkeys(existing))

        # 2) Configurar label_from_instance para todos los selects, incluyendo empresa
        related = {
            'id_tipo':         (EveTipos,       'nombre', EveTipos.objects.filter(activo='SI')),
            'id_subtipo':      (EveSubtipos,    'nombre', EveSubtipos.objects.filter(activo='SI')),
            'id_procedencia':  (EveProcedencias,'nombre', EveProcedencias.objects.filter(activo='SI')),
            'id_comuna':       (AdmComunas,     'nombre', AdmComunas.objects.filter(activo='SI')),
            'id_estado_actual':(EveEstados,     'nombre', EveEstados.objects.filter(activo='SI')),
            'empresa':         (EmpEmpresas,    'nombre', EmpEmpresas.objects.filter(activo='SI')),
        }
        for field_name, (model, attr, qs) in related.items():
            self.fields[field_name].queryset = qs
            self.fields[field_name].label_from_instance = lambda obj, attr=attr: getattr(obj, attr)

        # 3) Iniciales para nuevos registros
        if not self.instance.pk:
            now = datetime.now()
            self.fields['fecha'].initial         = now.date().strftime('%Y-%m-%d')
            self.fields['hora'].initial          = now.strftime('%H:%M')
            self.fields['alerta_encendida'].initial = 'SI'
            self.fields['fecha_alerta'].initial  = now
            self.fields['fecha_registro'].initial= now
        # Asegurar ocultos no obligatorios
        for hidden in ('alerta_encendida', 'fecha_alerta', 'fecha_registro'):
            self.fields[hidden].required = False

        # 4) Filtrar sucursales por empresa
        if 'empresa' in self.data:
            try:
                eid = int(self.data.get('empresa'))
                self.fields['id_sucursal'].queryset = EmpSucursales.objects.filter(id_empresa_id=eid)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.id_sucursal:
            self.fields['empresa'].initial = self.instance.id_sucursal.id_empresa
            self.fields['id_sucursal'].queryset = EmpSucursales.objects.filter(
                id_empresa=self.instance.id_sucursal.id_empresa
            )

        # 5) Manejo de subtipo dinámico
        if tipo_evento_id:
            self.cargar_subtipos(tipo_evento_id)
            self.fields['id_tipo'].widget = forms.HiddenInput()
            self.fields['id_tipo'].disabled = True
        else:
            self.fields['id_subtipo'].queryset = EveSubtipos.objects.none()
            if 'id_tipo' in self.data:
                try:
                    t = int(self.data.get('id_tipo'))
                    self.cargar_subtipos(t)
                except (ValueError, TypeError):
                    pass

    def cargar_subtipos(self, tipo_id):
        try:
            tipo = EveTipos.objects.get(pk=tipo_id)
            self.fields['id_subtipo'].queryset = EveSubtipos.objects.filter(id_tipo_id=tipo_id)
            self.fields['id_tipo'].initial = tipo
        except EveTipos.DoesNotExist:
            self.fields['id_subtipo'].queryset = EveSubtipos.objects.none()

    def clean_alerta_encendida(self):
        return self.cleaned_data.get('alerta_encendida', 'SI')

    def clean_fecha_alerta(self):
        return self.cleaned_data.get('fecha_alerta', datetime.now())

    def clean_fecha_registro(self):
        return self.cleaned_data.get('fecha_registro', datetime.now())

    def clean(self):
        cd = super().clean()
        # Validar coordenadas
        lat, lon = cd.get('latitud'), cd.get('longitud')
        try:
            if lat and not -90 <= float(lat) <= 90:
                self.add_error('latitud', "Valor debe estar entre -90 y 90")
            if lon and not -180 <= float(lon) <= 180:
                self.add_error('longitud', "Valor debe estar entre -180 y 180")
        except ValueError:
            self.add_error('latitud', "Formato inválido para coordenadas")
            self.add_error('longitud', "Formato inválido para coordenadas")
        # Validar fecha_alerta vs fecha evento
        if cd.get('fecha_alerta') and cd['fecha_alerta'].date() < cd.get('fecha'):
            self.add_error('fecha_alerta', "La alerta no puede ser anterior al evento")
        # Relación tipo-subtipo
        if not cd.get('id_tipo') and cd.get('id_subtipo'):
            self.add_error('id_subtipo', "Debe seleccionar un tipo primero")
        return cd

    def save(self, commit=True):
        instance = super().save(commit=False)
        now = datetime.now()
        if not instance.alerta_encendida:
            instance.alerta_encendida = 'SI'
        if not instance.fecha_alerta:
            instance.fecha_alerta = now
        if not instance.fecha_registro:
            instance.fecha_registro = now
        if commit:
            instance.save()
        return instance
