from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from .models import DisTiposDispositivos, DisTiposSensores, DisCompaniasSim, DisTiposSim,DisDispositivos
from django.views.decorators.http import require_POST
from apps.usuarios.decorators import groups_required

# --------- Tipos de Dispositivos ---------
def listar_tipos_dispositivos(request):
    tipos = DisTiposDispositivos.objects.all()
    context = {
        'page_obj': tipos,
        'mostrar': tipos,
    }
    return render(request, 'dispositivos/tipos_dispositivos_list.html', context)

@groups_required('Administrador, Editor', login_url='usuarios:sin_permiso')
def editar_tipo_dispositivo(request):
    if request.method == 'POST':
        tipo = get_object_or_404(DisTiposDispositivos, pk=request.POST.get('id_tipo_dispositivo'))
        tipo.nombre = request.POST.get('nombre')
        tipo.activo = request.POST.get('activo')
        tipo.save()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'id': tipo.id_tipo_dispositivo,
                'nombre': tipo.nombre,
                'activo': tipo.activo
            })
        return redirect('dispositivo:listar_tipos_dispositivos')
    return JsonResponse({'success': False}, status=400)

@groups_required('Administrador, Editor', login_url='usuarios:sin_permiso')
def agregar_tipo_dispositivo(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        activo = request.POST.get('activo')
        tipo = DisTiposDispositivos.objects.create(nombre=nombre, activo=activo)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Corrige aquí el nombre exacto de tu campo pk si es diferente
            return JsonResponse({
                'success': True,
                'id_tipo_dispositivo': tipo.id_tipo_dispositivo,  # <-- asegúrate que es este nombre!
                'nombre': tipo.nombre,
                'activo': tipo.activo,
            })
        return redirect('dispositivo:listar_tipos_dispositivos')
    return HttpResponseBadRequest("Método no permitido")


# --------- Tipos de Sensores ---------
def listar_tipos_sensores(request):
    tipos = DisTiposSensores.objects.all()
    context = {
        'page_obj': tipos,
        'mostrar': tipos,
    }
    return render(request, 'dispositivos/tipos_sensores_list.html', context)

@groups_required('Administrador, Editor', login_url='usuarios:sin_permiso')
def editar_tipo_sensor(request):
    if request.method == 'POST':
        sensor = get_object_or_404(DisTiposSensores, pk=request.POST.get('id_tipo_sensor'))
        sensor.nombre = request.POST.get('nombre')
        sensor.activo = request.POST.get('activo')
        sensor.save()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'id': sensor.id_tipo_sensor,
                'nombre': sensor.nombre,
                'activo': sensor.activo
            })
        return redirect('dispositivo:listar_tipos_sensores')
    return JsonResponse({'success': False}, status=400)

@groups_required('Administrador, Editor', login_url='usuarios:sin_permiso')
def agregar_tipo_sensor(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        activo = request.POST.get('activo')
        sensor = DisTiposSensores.objects.create(nombre=nombre, activo=activo)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'id': sensor.id_tipo_sensor,
                'nombre': sensor.nombre,
                'activo': sensor.activo
            })
        return redirect('dispositivo:listar_tipos_sensores')
    return HttpResponseBadRequest("Método no permitido")

# --------- Compañías SIM ---------
def listar_companias_sim(request):
    companias = DisCompaniasSim.objects.all()
    context = {
        'page_obj': companias,
        'mostrar': companias,
    }
    return render(request, 'dispositivos/companias_sim_list.html', context)

@groups_required('Administrador, Editor', login_url='usuarios:sin_permiso')
def editar_compania_sim(request):
    if request.method == 'POST':
        compania = get_object_or_404(DisCompaniasSim, pk=request.POST.get('id_compania_sim'))
        compania.nombre = request.POST.get('nombre')
        compania.activo = request.POST.get('activo')
        compania.save()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'id': compania.id_compania_sim,
                'nombre': compania.nombre,
                'activo': compania.activo
            })
        return redirect('dispositivo:listar_companias_sim')
    return JsonResponse({'success': False}, status=400)

@groups_required('Administrador, Editor', login_url='usuarios:sin_permiso')
def agregar_compania_sim(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        activo = request.POST.get('activo')
        compania = DisCompaniasSim.objects.create(nombre=nombre, activo=activo)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'id': compania.id_compania_sim,
                'nombre': compania.nombre,
                'activo': compania.activo
            })
        return redirect('dispositivo:listar_companias_sim')
    return HttpResponseBadRequest("Método no permitido")


# --------- Tipos de SIM ---------
def listar_tipos_sim(request):
    tipos = DisTiposSim.objects.all()
    context = {
        'page_obj': tipos,
        'mostrar': tipos,
    }
    return render(request, 'dispositivos/tipos_sim_list.html', context)

@groups_required('Administrador, Editor', login_url='usuarios:sin_permiso')
def editar_tipo_sim(request):
    if request.method == 'POST':
        tipo = get_object_or_404(DisTiposSim, pk=request.POST.get('id_tipo_sim'))
        tipo.nombre = request.POST.get('nombre')
        tipo.activo = request.POST.get('activo')
        tipo.save()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'id': tipo.id_tipo_sim,
                'nombre': tipo.nombre,
                'activo': tipo.activo
            })
        return redirect('dispositivo:listar_tipos_sim')
    return JsonResponse({'success': False}, status=400)

@groups_required('Administrador, Editor', login_url='usuarios:sin_permiso')
def agregar_tipo_sim(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        activo = request.POST.get('activo')
        tipo = DisTiposSim.objects.create(nombre=nombre, activo=activo)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'id_tipo_sim': tipo.id_tipo_sim,  # o el campo pk correspondiente
                'nombre': tipo.nombre,
                'activo': tipo.activo,
            })
        return redirect('dispositivo:listar_tipos_sim')
    return HttpResponseBadRequest("Método no permitido")


##########################

def listar_dispositivos(request):
    dispositivos = DisDispositivos.objects.select_related(
        'id_tipo_dispositivo', 'id_compania_sim', 'id_tipo_sim'
    ).all().order_by('numero_serie')

    tipos = DisTiposDispositivos.objects.filter(activo='SI').order_by('nombre')
    companias = DisCompaniasSim.objects.filter(activo='SI').order_by('nombre')
    tipos_sim = DisTiposSim.objects.filter(activo='SI').order_by('nombre')

    context = {
        'page_obj': dispositivos,
        'tipos': tipos,
        'companias': companias,
        'tipos_sim': tipos_sim,
    }
    return render(request, 'dispositivos/dispositivos_list.html', context)


@groups_required('Administrador, Editor', login_url='usuarios:sin_permiso')
@require_POST
def editar_dispositivo(request, id_dispositivo):
    dispositivo = get_object_or_404(DisDispositivos, pk=id_dispositivo)
    dispositivo.numero_serie = request.POST.get('numero_serie')
    dispositivo.id_tipo_dispositivo_id = request.POST.get('id_tipo_dispositivo')
    dispositivo.telefono = request.POST.get('telefono')
    dispositivo.id_compania_sim_id = request.POST.get('id_compania_sim') or None
    dispositivo.id_tipo_sim_id = request.POST.get('id_tipo_sim') or None
    dispositivo.endpoint_1 = request.POST.get('endpoint_1')
    dispositivo.endpoint_2 = request.POST.get('endpoint_2')
    dispositivo.save()

    return JsonResponse({
        'success': True,
        'dispositivo': {
            'id': dispositivo.id_dispositivo,
            'numero_serie': dispositivo.numero_serie,
            'tipo': dispositivo.id_tipo_dispositivo.nombre if dispositivo.id_tipo_dispositivo else '',
            'id_tipo_dispositivo': dispositivo.id_tipo_dispositivo.id_tipo_dispositivo if dispositivo.id_tipo_dispositivo else '',
            'telefono': dispositivo.telefono,
            'compania': dispositivo.id_compania_sim.nombre if dispositivo.id_compania_sim else '',
            'id_compania_sim': dispositivo.id_compania_sim.id_compania_sim if dispositivo.id_compania_sim else '',
            'tipo_sim': dispositivo.id_tipo_sim.nombre if dispositivo.id_tipo_sim else '',
            'id_tipo_sim': dispositivo.id_tipo_sim.id_tipo_sim if dispositivo.id_tipo_sim else '',
            'endpoint_1': dispositivo.endpoint_1 or '',
            'endpoint_2': dispositivo.endpoint_2 or '',
        }
    })
    
    
@groups_required('Administrador, Editor', login_url='usuarios:sin_permiso')
@require_POST
def agregar_dispositivo(request):
    numero_serie = request.POST.get('numero_serie')
    id_tipo = request.POST.get('id_tipo_dispositivo')
    telefono = request.POST.get('telefono')
    id_compania = request.POST.get('id_compania_sim')
    id_tipo_sim = request.POST.get('id_tipo_sim')
    endpoint_1 = request.POST.get('endpoint_1')
    endpoint_2 = request.POST.get('endpoint_2')

    # Validaciones mínimas
    if not numero_serie or not id_tipo:
        return JsonResponse({'success': False, 'errors': 'Faltan campos obligatorios'})

    dispositivo = DisDispositivos.objects.create(
        numero_serie=numero_serie,
        id_tipo_dispositivo_id=id_tipo,
        telefono=telefono,
        id_compania_sim_id=id_compania if id_compania else None,
        id_tipo_sim_id=id_tipo_sim if id_tipo_sim else None,
        endpoint_1=endpoint_1,
        endpoint_2=endpoint_2,
    )

    # Preparar el objeto para la DataTable
    return JsonResponse({
        'success': True,
        'dispositivo': {
            'id': dispositivo.id_dispositivo,
            'numero_serie': dispositivo.numero_serie,
            'tipo': dispositivo.id_tipo_dispositivo.nombre if dispositivo.id_tipo_dispositivo else '',
            'id_tipo_dispositivo': dispositivo.id_tipo_dispositivo.id_tipo_dispositivo if dispositivo.id_tipo_dispositivo else '',
            'telefono': dispositivo.telefono,
            'compania': dispositivo.id_compania_sim.nombre if dispositivo.id_compania_sim else '',
            'id_compania_sim': dispositivo.id_compania_sim.id_compania_sim if dispositivo.id_compania_sim else '',
            'tipo_sim': dispositivo.id_tipo_sim.nombre if dispositivo.id_tipo_sim else '',
            'id_tipo_sim': dispositivo.id_tipo_sim.id_tipo_sim if dispositivo.id_tipo_sim else '',
            'endpoint_1': dispositivo.endpoint_1 or '',
            'endpoint_2': dispositivo.endpoint_2 or '',
        }
    })
