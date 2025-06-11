from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import AdmEstadosCiviles, AdmGenero
from django.views.decorators.csrf import csrf_exempt

### Estado civil


def listar_estados_civiles(request):
    # Se listan todos los estados civiles sin paginación
    estados_civiles = AdmEstadosCiviles.objects.all().order_by('nombre')
    context = {
        'estados_civiles': estados_civiles,
    }
    return render(request, 'mantenedores/estados_civiles_list.html', context)

def editar_estado(request):
    if request.method == 'POST':
        estado = get_object_or_404(AdmEstadosCiviles, pk=request.POST.get('id_estado_civil'))
        estado.nombre = request.POST.get('nombre')
        estado.activo = request.POST.get('activo')
        estado.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def agregar_estado(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        activo = request.POST.get('activo')
        nuevo = AdmEstadosCiviles.objects.create(nombre=nombre, activo=activo)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Devuelve JSON para AJAX
            return JsonResponse({
                'success': True,
                'id_estado_civil': nuevo.id_estado_civil,
                'nombre': nuevo.nombre,
                'activo': nuevo.activo,
            })
        # Si no es AJAX, redirecciona normalmente
        return redirect('mantenedor:listar_estados_civiles')
    # Si no es POST, responde error
    return JsonResponse({'success': False}, status=400)



### ------------------------

### Genero

def listar_genero(request):
    # Se listan todos los géneros sin paginación
    generos = AdmGenero.objects.all().order_by('nombre')
    context = {
        'page_genero': generos,
        'mostrar': generos,
    }
    return render(request, 'mantenedores/genero_list.html', context)

def editar_genero(request):
    if request.method == 'POST':
        genero = get_object_or_404(AdmGenero, pk=request.POST.get('id_genero'))
        genero.nombre = request.POST.get('nombre')
        genero.activo = request.POST.get('activo')
        genero.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def agregar_genero(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        activo = request.POST.get('activo')
        nuevo = AdmGenero.objects.create(nombre=nombre, activo=activo)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'id_genero': nuevo.id_genero,
                'nombre': nuevo.nombre,
                'activo': nuevo.activo,
            })
        return redirect('mantenedor:listar_genero')
    return JsonResponse({'success': False}, status=400)

