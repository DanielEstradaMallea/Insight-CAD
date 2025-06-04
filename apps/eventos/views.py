from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import EveEventos,EveTipos, EveImagenesEventos, EveProcedencias, EveEstados, EveSubtipos,EveAntecedentesEventos, EveEstadosEventos
from datetime import date, timedelta, datetime
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone


#########################################################################################    
### Eventos
def reporte_eventos(request):
    """
    Renderiza el template principal del reporte de eventos.
    """
    return render(request, 'eventos/reporte_eventos.html')


def cargar_tipos_eventos(request):
    """
    Retorna los tipos de eventos en formato JSON.
    """
    tipos = EveTipos.objects.filter(activo='SI').order_by('nombre').values('id_tipo', 'nombre')
    return JsonResponse(list(tipos), safe=False)

def cargar_subtipos_eventos(request):
    """
    Retorna los subtipos de un tipo de evento específico en formato JSON.
    """
    id_tipo = request.GET.get('id_tipo')
    subtipos = EveSubtipos.objects.filter(id_tipo=id_tipo).order_by('nombre').values(
        'id_subtipo', 'nombre', 'id_tipo__nombre', 'prioridad', 'activo'
    )
    return JsonResponse(list(subtipos), safe=False)




def obtener_eventos_filtrados(request):
    """
    Filtra los eventos según el tipo de evento y rango de fechas, SIN paginación.
    """
    tipo_evento = request.GET.get('tipo_evento')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    if not fecha_inicio or not fecha_fin:
        fecha_fin = datetime.now().date()
        fecha_inicio = fecha_fin - timedelta(days=30)
    else:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()

    # Filtrar los eventos en base a los parámetros
    filtros = {
        'fecha__range': [fecha_inicio, fecha_fin]
    }
    if tipo_evento:  # Solo si viene un tipo válido
        filtros['id_tipo'] = tipo_evento

    eventos = EveEventos.objects.filter(**filtros).order_by('-fecha', '-hora').values(
        'id_evento', 'nombre', 'id_tipo__nombre', 'id_subtipo__nombre', 'tipo_evento',
        'fecha', 'hora', 'direccion', 'latitud', 'longitud', 'detalle', 'id_comuna__nombre',
        'id_sucursal__nombre', 'id_dispositivo', 'id_sensor', 'id_estado_actual__nombre',
        'alerta_encendida', 'fecha_alerta', 'fecha_registro', 'observaciones_cierre',
        'id_subtipo__prioridad'
    )

    data = {
        'eventos': list(eventos)
    }

    return JsonResponse(data, safe=False)


def obtener_detalle_evento(request, evento_id):
    try:
        evento = EveEventos.objects.select_related(
            'id_tipo', 'id_subtipo', 'id_procedencia', 'id_comuna', 'id_estado_actual'
        ).get(id_evento=evento_id)
        
        data = {
            'nombre': evento.nombre,
            'tipo': evento.id_tipo.nombre if evento.id_tipo else 'N/A',
            'subtipo': evento.id_subtipo.nombre if evento.id_subtipo else 'N/A',
            'procedencia': evento.id_procedencia.nombre if evento.id_procedencia else 'N/A',
            'estado': evento.id_estado_actual.nombre if evento.id_estado_actual else 'N/A',
            'detalle': evento.detalle,
            'fecha': evento.fecha.strftime("%d/%m/%Y"),
            'hora': evento.hora.strftime("%H:%M") if evento.hora else 'N/A',
            'direccion': evento.direccion,
            'comuna': evento.id_comuna.nombre if evento.id_comuna else 'N/A',
            'latitud': evento.latitud,
            'longitud': evento.longitud,
            'registrado': evento.id_usuario.username if evento.id_usuario else 'N/A'
            
        }
        return JsonResponse(data)
    except EveEventos.DoesNotExist:
        return JsonResponse({'error': 'Evento no encontrado'}, status=404)


#########################################################################################    
### Enviar Evento

from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import EveEventos
from .forms import EventoForm

class EventoCreateView(LoginRequiredMixin, CreateView):
    model         = EveEventos
    form_class    = EventoForm
    template_name = 'eventos/nuevo_evento.html'
    success_url   = reverse_lazy('evento:reporte_eventos')
    login_url     = 'usuarios:login'

    def form_valid(self, form):
        print(">>> form_valid INICIADO, request.FILES =", self.request.FILES)
        form.instance.id_usuario = self.request.user
        response = super().form_valid(form)

        # DEBUG servidor: ¿llega algo?
        archivos = self.request.FILES.getlist('imagenes')
        print("📂 Archivos recibidos en form_valid:", archivos)

        for archivo in archivos:
            print("🔄 Subiendo:", archivo.name)
            img = EveImagenesEventos(
                id_evento=self.object,
                nombre=archivo.name
            )
            img.archivo.save(archivo.name, archivo, save=False)
            img.save()
            print("✅ Subido:", img.archivo.url)

        return response

    def form_invalid(self, form):
        # Opcional: imprimir errores en consola
        print("❌ Errores en el formulario:", form.errors)
        return super().form_invalid(form)
#########################################################################################    
### Tipo Evento


def listar_tipo_evento(request):
        

    tipo_evento = EveTipos.objects.all().order_by('nombre')

    # Paginar resultados
    paginator = Paginator(tipo_evento, 50)  # 10 registros por página
    page_number = request.GET.get('page')
    page_tipo = paginator.get_page(page_number)

    context = {
        'page_tipo': page_tipo,
        'mostrar': tipo_evento,
    }
    return render(request, 'eventos/tipo_evento.html', context)

def mostrar_subtipo_evento(request):        
    
    return render(request, 'eventos/subtipo_evento.html')




def editar_tipo_evento(request):
    if request.method == 'POST':
        estado = get_object_or_404(EveTipos, pk=request.POST.get('id_tipo_evento'))
        estado.nombre = request.POST.get('nombre')
        estado.activo = request.POST.get('activo')
        estado.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})



def agregar_tipo_evento(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        activo = request.POST.get('activo')
        EveTipos.objects.create(nombre=nombre, activo=activo)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

    


def obtener_imagenes_evento(request, evento_id):
    imagenes = EveImagenesEventos.objects.filter(id_evento=evento_id)
    payload = {"imagenes": []}

    for img in imagenes:
        # img.archivo.url respetará tu MEDIA_URL y DefaultFileStorage (S3 o local)
        url_absoluta = request.build_absolute_uri(img.archivo.url)
        payload["imagenes"].append({
            "url":    url_absoluta,
            "nombre": img.nombre or ""
        })

    return JsonResponse(payload)

#########################################################################################
### Procedencias

def listar_procedencias(request):
    procedencias = EveProcedencias.objects.all().order_by('nombre')
    context = {
        'procedencias': procedencias,
    }
    return render(request, 'eventos/procedencias_list.html', context)

def editar_procedencia(request):
    try:
        procedencia = get_object_or_404(EveProcedencias, pk=request.POST.get('id_procedencia'))
        procedencia.nombre = request.POST.get('nombre')
        procedencia.activo = request.POST.get('activo')
        procedencia.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def agregar_procedencia(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        activo = request.POST.get('activo')
        try:
            EveProcedencias.objects.create(nombre=nombre, activo=activo)
            # Si la petición es AJAX (JS), responder JSON para el template institucional
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            else:
                return redirect('evento:listar_procedencias')
        except Exception as e:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            else:
                return redirect('evento:listar_procedencias')
    # Si no es POST
    return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
#########################################################################################
### Estados reporte

### Estados
def listar_estados(request):
    estados = EveEstados.objects.all().order_by('nombre')
    context = {
        'estados': estados,
    }
    return render(request, 'eventos/estados_list.html', context)

def editar_estado(request):
    if request.method == 'POST':
        estado = get_object_or_404(EveEstados, pk=request.POST.get('id_estado'))
        estado.nombre = request.POST.get('nombre')
        estado.activo = request.POST.get('activo')
        estado.save()
        # Retornamos JSON para poder manejar la respuesta vía AJAX en el modal
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def agregar_estado(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        activo = request.POST.get('activo')
        EveEstados.objects.create(nombre=nombre, activo=activo)
        return JsonResponse({'success': True})  # <--- ESTA LÍNEA SOLUCIONA TU PROBLEMA
    return JsonResponse({'success': False})
    


#########################################################################################
### Subtipos Form
def get_subtipos(request):
    tipo_id = request.GET.get('tipo_id')
    subtipos = EveSubtipos.objects.filter(
        id_tipo_id=tipo_id,
        activo='SI'  # Añadir filtro de activos
    ).values('id_subtipo', 'nombre')
    return JsonResponse(list(subtipos), safe=False)

def cargar_subtipos(self, tipo_id):
    try:
        tipo = EveTipos.objects.get(pk=tipo_id)
        self.fields['id_subtipo'].queryset = EveSubtipos.objects.filter(
            id_tipo=tipo,
            activo='SI'  # Añadir filtro de activos
        )
        self.fields['id_tipo'].initial = tipo
    except EveTipos.DoesNotExist:
        self.fields['id_subtipo'].queryset = EveSubtipos.objects.none()
        
def agregar_subtipo(request):
    if request.method == 'POST':
        id_tipo = request.POST.get('id_tipo')
        nombre = request.POST.get('nombre')
        prioridad = request.POST.get('prioridad')
        activo = request.POST.get('activo')

        tipo = EveTipos.objects.get(id_tipo=id_tipo)
        subtipo = EveSubtipos.objects.create(
            nombre=nombre,
            id_tipo=tipo,
            prioridad=prioridad,
            activo=activo
        )
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def editar_subtipo(request):
    """
    Edita un subtipo existente.
    """
    if request.method == 'POST':
        id_subtipo = request.POST.get('id_subtipo')
        nombre = request.POST.get('nombre')
        prioridad = request.POST.get('prioridad')
        activo = request.POST.get('activo')
        try:
            subtipo = EveSubtipos.objects.get(id_subtipo=id_subtipo)
            subtipo.nombre = nombre
            subtipo.prioridad = prioridad
            subtipo.activo = activo
            subtipo.save()
            return JsonResponse({'success': True})
        except EveSubtipos.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Subtipo no encontrado'})
    return JsonResponse({'success': False})

def eliminar_subtipo(request):
    """
    Elimina un subtipo existente.
    """
    if request.method == 'POST':
        id_subtipo = request.POST.get('id_subtipo')
        try:
            subtipo = EveSubtipos.objects.get(id_subtipo=id_subtipo)
            subtipo.delete()
            return JsonResponse({'success': True})
        except EveSubtipos.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Subtipo no encontrado'})
    return JsonResponse({'success': False})

#########################################################################################
### Alerta btn
@require_POST
def cambiar_estado_alerta(request, evento_id):
    try:
        evento = EveEventos.objects.get(id_evento=evento_id)
        nuevo_estado = request.POST.get('nuevo_estado')

        if nuevo_estado in ['SI', 'NO']:
            evento.alerta_encendida = nuevo_estado
            evento.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Estado inválido'})
    except EveEventos.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Evento no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


#########################################################################################
### Antecedentes

from .models import EveAntecedentesEventos

def obtener_antecedentes(request, evento_id):
    """Obtiene los antecedentes de un evento específico."""
    try:
        antecedentes = EveAntecedentesEventos.objects.filter(id_evento=evento_id).values(
            'id_antecedente', 'antecedente', 'fecha', 'hora', 'id_usuario'
        )
        return JsonResponse({'antecedentes': list(antecedentes)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_POST
def guardar_antecedente(request, evento_id):
    try:
        # Imprimir datos recibidos para depuración
        print("Datos recibidos:", request.POST)

        antecedente = request.POST.get('antecedente')
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        id_usuario = 1  # Asume que el usuario siempre es 1

        # Validar campos obligatorios
        if not antecedente or not fecha or not hora:
            return JsonResponse({'success': False, 'error': 'Faltan campos obligatorios'})

        # Crear y guardar el antecedente
        nuevo_antecedente = EveAntecedentesEventos(
            id_evento_id=evento_id,
            antecedente=antecedente,
            fecha=fecha,
            hora=hora,
            id_usuario_id=id_usuario,
            fecha_registro=timezone.now()
        )
        nuevo_antecedente.save()

        return JsonResponse({'success': True})
    except Exception as e:
        # Imprimir el error para depuración
        print("Error al guardar antecedente:", str(e))
        return JsonResponse({'success': False, 'error': str(e)})

#########################################################################################
### Estados

def obtener_estados(request):
    try:
        estados = EveEstados.objects.filter(activo='SI').values('id_estado', 'nombre')
        return JsonResponse({'estados': list(estados)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_POST
def cambiar_estado_evento(request, evento_id):
    try:
        nuevo_estado_id = request.POST.get('nuevo_estado_id')
        evento = EveEventos.objects.get(id_evento=evento_id)
        nuevo_estado = EveEstados.objects.get(id_estado=nuevo_estado_id)

        # Cambiar el estado del evento
        evento.id_estado_actual = nuevo_estado
        evento.save()

        # Registrar el cambio en EveEstadosEventos
        EveEstadosEventos.objects.create(
            id_evento=evento,
            id_estado=nuevo_estado,
            id_usuario_id=1,  # Asume que el usuario siempre es 1; reemplaza según corresponda
            fecha_registro=timezone.now()
        )

        return JsonResponse({
            'success': True,
            'nuevo_estado': {'nombre': nuevo_estado.nombre}
        })
    except EveEventos.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Evento no encontrado'}, status=404)
    except EveEstados.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Estado no válido'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def obtener_historial_estados(request, evento_id):
    try:
        historial = EveEstadosEventos.objects.filter(id_evento=evento_id).select_related('id_estado').values(
            'id_estado__nombre', 'fecha_registro', 'id_usuario'
        )
        return JsonResponse({'historial': list(historial)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)