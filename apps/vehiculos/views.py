from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import VehVehiculos,VehTiposVehiculos, VehMarcasVehiculos,Cuadrilla, Asignacion
from .forms import VehVehiculoForm
from django.views.decorators.http import require_http_methods
from apps.eventos.models import EveEventos

def vehiculos_list(request):
    query = request.GET.get('search', '')
    vehiculos = VehVehiculos.objects.filter(patente__icontains=query) if query else VehVehiculos.objects.all().order_by('patente')
    paginator = Paginator(vehiculos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    marcas = VehMarcasVehiculos.objects.filter(activo='SI').order_by('nombre')
    tipos = VehTiposVehiculos.objects.filter(activo='SI').order_by('nombre')
    return render(request, 'vehiculos/vehiculos_list.html', {
        'page_obj': page_obj,
        'marcas': marcas,
        'tipos': tipos,
    })

def agregar_vehiculo(request):
    if request.method == 'POST':
        data = request.POST.copy()
        data['activo'] = 'SI'
        data['lista_gris'] = 'NO'
        data['id_usuario'] = 1
        form = VehVehiculoForm(data)
        if form.is_valid():
            vehiculo = form.save()
            return JsonResponse({
                'success': True,
                'vehiculo': {
                    'id': vehiculo.id_vehiculo,
                    'patente': vehiculo.patente,
                    'marca': vehiculo.id_marca_vehiculo.nombre,
                    'modelo': vehiculo.modelo,
                    'color': vehiculo.color,
                    'tipo': vehiculo.id_tipo_vehiculo.nombre,
                }
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

def modificar_vehiculo(request, id_vehiculo):
    vehiculo = get_object_or_404(VehVehiculos, id_vehiculo=id_vehiculo)
    if request.method == 'POST':
        data = request.POST.copy()

        # Si los campos no vienen del formulario, los tomamos del modelo actual
        if not data.get('lista_gris'):
            data['lista_gris'] = vehiculo.lista_gris
        if not data.get('activo'):
            data['activo'] = vehiculo.activo
        if not data.get('id_usuario'):
            data['id_usuario'] = 1  # O el ID fijo si aplica

        form = VehVehiculoForm(data, instance=vehiculo)
        if form.is_valid():
            vehiculo = form.save()
            return JsonResponse({
                'success': True,
                'vehiculo': {
                    'id': vehiculo.id_vehiculo,
                    'patente': vehiculo.patente,
                    'marca': vehiculo.id_marca_vehiculo.nombre if vehiculo.id_marca_vehiculo else '',
                    'modelo': vehiculo.modelo,
                    'color': vehiculo.color,
                    'tipo': vehiculo.id_tipo_vehiculo.nombre if vehiculo.id_tipo_vehiculo else '',
                }
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

# ----- Tipos de Vehículo -----
def listar_tipos_vehiculos(request):
    tipos = VehTiposVehiculos.objects.all()
    context = {
        'page_obj': tipos,
        'mostrar': tipos,
    }
    return render(request, 'vehiculos/tipos_vehiculos_list.html', context)

def editar_tipo_vehiculo(request):
    if request.method == 'POST':
        tipo = get_object_or_404(VehTiposVehiculos, pk=request.POST.get('id_tipo_vehiculo'))
        tipo.nombre = request.POST.get('nombre')
        tipo.activo = request.POST.get('activo')
        tipo.save()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'id_tipo_vehiculo': tipo.id_tipo_vehiculo,
                'nombre': tipo.nombre,
                'activo': tipo.activo,
            })
        return redirect('vehiculos:listar_tipos_vehiculos')
    return JsonResponse({'success': False}, status=400)

def agregar_tipo_vehiculo(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        activo = request.POST.get('activo')
        tipo = VehTiposVehiculos.objects.create(nombre=nombre, activo=activo)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'id_tipo_vehiculo': tipo.id_tipo_vehiculo,
                'nombre': tipo.nombre,
                'activo': tipo.activo,
            })
        return redirect('vehiculos:listar_tipos_vehiculos')
    return HttpResponseBadRequest("Método no permitido")

# ----- Marcas de Vehículo -----
def listar_marcas_vehiculos(request):
    marcas_vehiculos = VehMarcasVehiculos.objects.all()
    context = {
        'page_obj': marcas_vehiculos,
        'mostrar': marcas_vehiculos,
    }
    return render(request, 'vehiculos/marcas_vehiculos_list.html', context)

def editar_marca_vehiculo(request):
    if request.method == 'POST':
        marca = get_object_or_404(VehMarcasVehiculos, pk=request.POST.get('id_marca_vehiculo'))
        marca.nombre = request.POST.get('nombre')
        marca.activo = request.POST.get('activo')
        marca.save()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'id_marca_vehiculo': marca.id_marca_vehiculo,
                'nombre': marca.nombre,
                'activo': marca.activo,
            })
        return redirect('vehiculos:listar_marcas_vehiculos')
    return JsonResponse({'success': False}, status=400)

def agregar_marca_vehiculo(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        activo = request.POST.get('activo')
        marca = VehMarcasVehiculos.objects.create(nombre=nombre, activo=activo)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'id_marca_vehiculo': marca.id_marca_vehiculo,
                'nombre': marca.nombre,
                'activo': marca.activo,
            })
        return redirect('vehiculos:listar_marcas_vehiculos')
    return HttpResponseBadRequest("Método no permitido")

    
########################
### buscador ajax 

def buscar_vehiculos(request):
    # Obtener los parámetros de búsqueda
    patente = request.GET.get('patente', '').strip()
    modelo = request.GET.get('modelo', '').strip()

    # Consultar todos los vehículos inicialmente
    vehiculos = VehVehiculos.objects.all()

    # Aplicar filtros dinámicos
    if patente:
        vehiculos = vehiculos.filter(Q(patente__icontains=patente))
    
    if modelo:
        vehiculos = vehiculos.filter(Q(modelo__icontains=modelo))

    # Formatear los resultados
    data = [{
        'id_vehiculo': v.id_vehiculo,
        'patente': v.patente,
        'marca': v.id_marca_vehiculo.nombre if v.id_marca_vehiculo else '-',
        'modelo': v.modelo,
        'color': v.color
    } for v in vehiculos.order_by('patente')[:50]]  # Limitar a 50 resultados

    # Devolver los datos como JSON
    return JsonResponse(data, safe=False)

###################################################
# Para obtener la asignación de un evento específico
def get_asignacion(request, evento_id):
    try:
        asignacion = Asignacion.objects.get(evento_id=evento_id, estado='asignado')
        data = {
            'evento': asignacion.evento.nombre,
            'cuadrilla': asignacion.cuadrilla.nombre,
            'estado': asignacion.estado,
            'ruta': asignacion.ruta,
            'cuadrilla_id': asignacion.cuadrilla.id,
        }
        return JsonResponse(data)
    except Asignacion.DoesNotExist:
        return JsonResponse({'error': 'No asignado'}, status=404)
    
def get_asignaciones(request):
    asignaciones = Asignacion.objects.all().values('id', 'evento__nombre', 'cuadrilla__nombre', 'estado')
    return JsonResponse(list(asignaciones), safe=False)    

@require_http_methods(["POST"])
def asignar_cuadrilla(request):
    evento_id = request.POST.get('evento_id')
    cuadrilla_id = request.POST.get('cuadrilla_id')
    try:
        evento = EveEventos.objects.get(id_evento=evento_id)
        cuadrilla = Cuadrilla.objects.get(id=cuadrilla_id)
        # Actualizar estado de la cuadrilla
        cuadrilla.estado = 'en_camino'
        cuadrilla.save()
        # Crear o actualizar la asignación
        asignacion, created = Asignacion.objects.update_or_create(
            evento=evento,
            defaults={'cuadrilla': cuadrilla, 'estado': 'asignado'}
        )
        return JsonResponse({'status': 'ok', 'asignacion_id': asignacion.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'error': str(e)}, status=400)

@require_http_methods(["POST"])
def cancelar_asistencia(request):
    asignacion_id = request.POST.get('asignacion_id')
    try:
        asignacion = Asignacion.objects.get(id=asignacion_id)
        asignacion.estado = 'cancelado'
        asignacion.save()
        # Actualizar la cuadrilla a estado disponible y, opcionalmente, actualizar su posición
        cuadrilla = asignacion.cuadrilla
        # Aquí podrías obtener la posición actual (en el futuro vía GPS)
        # Por ahora, asumiremos que se mantiene la posición del último movimiento
        cuadrilla.estado = 'disponible'
        cuadrilla.save()
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'error': str(e)}, status=400)