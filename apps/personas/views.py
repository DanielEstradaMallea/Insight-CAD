from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from .models import EveTiposPersonas, PerPersonas, PerPersonasGrises,Usuarios
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from .forms import PersonaForm
from django.utils import timezone

def listar_tipos_personas(request):
    # Listamos todos los tipos de personas sin paginación
    tipos_personas = EveTiposPersonas.objects.all()
    context = {
        'tipos_personas': tipos_personas,
    }
    return render(request, 'personas/tipos_personas_list.html', context)

def editar_tipo_persona(request):
    try:
        tipo_persona = get_object_or_404(EveTiposPersonas, pk=request.POST.get('id_tipo_persona'))
        tipo_persona.nombre = request.POST.get('nombre')
        tipo_persona.activo = request.POST.get('activo')
        tipo_persona.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def agregar_tipo_persona(request):
    nombre = request.POST.get('nombre')
    activo = request.POST.get('activo')
    try:
        EveTiposPersonas.objects.create(nombre=nombre, activo=activo)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        else:
            return redirect('persona:listar_tipos_personas')
    except Exception as e:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)})
        else:
            return redirect('persona:listar_tipos_personas')

# Nueva vista para obtener tipos de persona en JSON
def listar_tipos_personas_json(request):
    tipos = EveTiposPersonas.objects.filter(activo='SI').values('id_tipo_persona', 'nombre')
    return JsonResponse(list(tipos), safe=False)



######################################################################################
### Personas CRUD



class PersonaListView(ListView):
    model = PerPersonas
    template_name = 'personas/list.html'
    context_object_name = 'personas'
    

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('search', '')
        rut = self.request.GET.get('rut', '')

        if rut:
            queryset = queryset.filter(rut=rut)
        elif query:
            queryset = queryset.filter(
                Q(nombre__icontains=query) |
                Q(paterno__icontains=query) |
                Q(materno__icontains=query))
            
        queryset =queryset.order_by('nombre')
        return queryset

class PersonaCreateView(CreateView):
    model = PerPersonas
    form_class = PersonaForm
    template_name = 'personas/agregar.html'  # Página separada para agregar
    success_url = reverse_lazy('persona:list')
    
    def form_valid(self, form):
        # Asignar el valor 1 a id_usuario, solo se usara como bypass hasta resolver si cada persona creada se asignara al usuario que lo ingresó
        form.instance.id_usuario_id = 1  # Asignar el valor 1 al campo id_usuario
        return super().form_valid(form)

class PersonaUpdateView(UpdateView):
    model = PerPersonas
    form_class = PersonaForm
    template_name = 'personas/editar.html'  # Página separada para editar
    success_url = reverse_lazy('persona:list')

class PersonaDeleteView(DeleteView):
    model = PerPersonas
    success_url = reverse_lazy('persona:list')

######################################################################################
### Validacion run

from django.views import View
from django.http import JsonResponse
from .validators import validar_rut 
    
class ValidarRUTView(View):
    def post(self, request, *args, **kwargs):
        rut = request.POST.get('rut', '').strip()
        try:
            validar_rut(rut)  # Usa la función de validación existente
            return JsonResponse({'valido': True})
        except Exception as e:
            return JsonResponse({'valido': False, 'mensaje': str(e)})
        

######################################################################################
### Buscador Personas
        

def buscar_personas(request):
    nombre = request.GET.get('nombre', '')
    rut = request.GET.get('rut', '')

    personas = PerPersonas.objects.all()
    
    if nombre:
        personas = personas.filter(
            Q(nombre__icontains=nombre) |
            Q(paterno__icontains=nombre) |
            Q(materno__icontains=nombre)
        )
    
    if rut:
        personas = personas.filter(rut__icontains=rut)

    data = [{
        'id': p.id_persona,
        'rut': p.rut,
        'nombre': p.nombre,
        'paterno': p.paterno,
        'materno': p.materno
    } for p in personas.order_by('nombre')[:50]]

    return JsonResponse(data, safe=False)

######################################################################################
### Lista gris Personas

@require_http_methods(["GET", "POST"])
def lista_gris_view(request):
    if request.method == "POST" and request.is_ajax():
        # Se procesa la acción enviada por AJAX: 'agregar' o 'quitar'
        accion = request.POST.get('action')
        persona_id = request.POST.get('id_persona')
        persona = get_object_or_404(PerPersonas, id_persona=persona_id)
        usuario = get_object_or_404(Usuarios, id_usuario=1)  # Hardcodeado

        if accion == "agregar":
            PerPersonasGrises.objects.create(
                id_persona=persona,
                accion='AGREGAR',
                id_usuario=usuario,
                fecha_registro=timezone.now()
            )
        elif accion == "quitar":
            PerPersonasGrises.objects.create(
                id_persona=persona,
                accion='QUITAR',
                id_usuario=usuario,
                fecha_registro=timezone.now()
            )
        else:
            return JsonResponse({"status": "error", "message": "Acción no válida"})

        # Se consulta el último registro para determinar el estado actual de la persona
        ultimo_registro = PerPersonasGrises.objects.filter(id_persona=persona).order_by('-fecha_registro').first()
        esta_en_lista = ultimo_registro and ultimo_registro.accion.upper() == 'AGREGAR'

        return JsonResponse({"status": "success", "esta_en_lista": bool(esta_en_lista)})

    # Para peticiones GET: se listan todas las personas junto con su estado en la lista gris.
    personas = PerPersonas.objects.all()
    for persona in personas:
        ultimo_registro = PerPersonasGrises.objects.filter(id_persona=persona).order_by('-fecha_registro').first()
        persona.esta_en_lista = ultimo_registro and ultimo_registro.accion.upper() == 'AGREGAR'
    
    return render(request, "personas/lista_gris_personas.html", {"personas": personas})
