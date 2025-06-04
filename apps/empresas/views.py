from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.views.decorators.http import require_POST,require_http_methods
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.db import transaction
import logging

from .models import EmpEmpresas, EmpSucursales, EmpRedApoyo
from .forms import EmpresaForm, SucursalForm
from apps.mantenedores.models import AdmComunas
from .validators import validar_rut

logger = logging.getLogger(__name__)


class EmpresaListView(ListView):
    """
    Vista basada en clase para listar empresas.

    Muestra un listado paginado de instancias de EmpEmpresas, permitiendo filtrar por
    'rut' o por una búsqueda general en los campos 'nombre', 'rut' y 'nombre_representante'.
    """
    model = EmpEmpresas
    template_name = 'empresas/empresas.html'
    context_object_name = 'empresas'
   

    def get_queryset(self):
        """
        Obtiene el queryset de empresas aplicando filtros de búsqueda o rut según los parámetros GET.

        Returns:
            QuerySet: Lista filtrada y ordenada de empresas.
        """
        queryset = super().get_queryset()
        query = self.request.GET.get('search', '')
        rut = self.request.GET.get('rut', '')
        if rut:
            queryset = queryset.filter(rut=rut)
        elif query:
            queryset = queryset.filter(
                Q(nombre__icontains=query) |
                Q(rut__icontains=query) |
                Q(nombre_representante__icontains=query)
            )
        return queryset.order_by('nombre')


class EmpresaCreateView(CreateView):
    """
    Vista basada en clase para crear una nueva empresa.

    Utiliza el formulario EmpresaForm y, tras la creación exitosa, redirige a la lista de empresas.
    """
    model = EmpEmpresas
    form_class = EmpresaForm
    template_name = 'empresas/agregar_empresa.html'
    success_url = reverse_lazy('empresa:list-empresas')
    
    def form_valid(self, form):
        """
        Procesa el formulario válido y crea una nueva instancia de empresa.

        Se asigna temporalmente el id de usuario y se envuelve la operación en una transacción atómica.

        Args:
            form (Form): El formulario validado.

        Returns:
            HttpResponse: Redirección a la URL de éxito o respuesta de error en caso de fallo.
        """
        form.instance.id_usuario_id = 1  # Hardcodeado temporalmente
        try:
            with transaction.atomic():
                return super().form_valid(form)
        except Exception as e:
            logger.error("Error creating empresa: %s", e, exc_info=True)
            form.add_error(None, "Error interno al crear la empresa. Intente nuevamente más tarde.")
            return self.form_invalid(form)


class EmpresaUpdateView(UpdateView):
    """
    Vista basada en clase para actualizar una empresa existente.

    Utiliza el formulario EmpresaForm y, tras la actualización, redirige a la lista de empresas.
    """
    model = EmpEmpresas
    form_class = EmpresaForm
    template_name = 'empresas/editar_empresa.html'
    success_url = reverse_lazy('empresa:list-empresas')
    
    def form_valid(self, form):
        """
        Procesa el formulario válido para actualizar la empresa.

        La operación se envuelve en una transacción atómica.

        Args:
            form (Form): El formulario validado.

        Returns:
            HttpResponse: Redirección a la URL de éxito o respuesta de error en caso de fallo.
        """
        try:
            with transaction.atomic():
                return super().form_valid(form)
        except Exception as e:
            logger.error("Error updating empresa: %s", e, exc_info=True)
            form.add_error(None, "Error interno al actualizar la empresa.")
            return self.form_invalid(form)


class EmpresaDeleteView(DeleteView):
    """
    Vista basada en clase para eliminar una empresa.

    Utiliza una plantilla específica y redirige a la lista de empresas tras la eliminación.
    """
    model = EmpEmpresas
    template_name = 'empresas/eliminar-empresa.html'
    success_url = reverse_lazy('empresa:list-empresas')
    
    def delete(self, request, *args, **kwargs):
        """
        Elimina la empresa y redirige a la lista de empresas.

        Envuelve la operación en una transacción atómica y maneja posibles errores.

        Returns:
            HttpResponse: Redirección en caso de éxito o JsonResponse con error en caso de fallo.
        """
        try:
            with transaction.atomic():
                self.object = self.get_object()
                self.object.delete()
            return redirect(self.success_url)
        except Exception as e:
            logger.error("Error deleting empresa: %s", e, exc_info=True)
            return JsonResponse({'success': False, 'error': 'Error interno al eliminar la empresa.'}, status=500)


class ValidarRUTView(View):
    """
    Vista basada en clase para validar el RUT de una empresa.

    Recibe el RUT vía POST, lo valida usando la función 'validar_rut' y devuelve un JSON indicando si es válido.
    """
    def post(self, request, *args, **kwargs):
        """
        Valida el RUT enviado en la solicitud POST.

        Returns:
            JsonResponse: Resultado de la validación con código de estado HTTP.
        """
        rut = request.POST.get('rut', '').strip()
        try:
            validar_rut(rut)
            return JsonResponse({'valido': True}, status=200)
        except Exception as e:
            logger.error("Error validating RUT: %s", e, exc_info=True)
            return JsonResponse({'valido': False, 'mensaje': 'RUT inválido.'}, status=400)


def cargar_sucursales(request):
    """
    Carga y devuelve las sucursales asociadas a una empresa en formato JSON.

    Obtiene el parámetro 'empresa_id' de la solicitud GET y filtra las sucursales.

    Returns:
        JsonResponse: Lista de sucursales o mensaje de error en caso de fallo.
    """
    empresa_id = request.GET.get('empresa_id')
    try:
        sucursales = EmpSucursales.objects.filter(id_empresa_id=empresa_id).values('id_sucursal', 'nombre')
        return JsonResponse(list(sucursales), safe=False, status=200)
    except Exception as e:
        logger.error("Error loading sucursales: %s", e, exc_info=True)
        return JsonResponse({'error': 'Error al cargar sucursales.'}, status=500)


def listar_sucursales(request, empresa_id):
    """
    Lista las sucursales de una empresa.
    
    Carga la empresa, las sucursales y las comunas (para los formularios de creación/edición).
    """
    empresa = get_object_or_404(EmpEmpresas, id_empresa=empresa_id)
    sucursales = EmpSucursales.objects.filter(id_empresa_id=empresa_id).order_by('nombre')
    comunas = AdmComunas.objects.all()
    form = SucursalForm()  # Formulario vacío para agregar sucursal
    context = {
        'empresa': empresa,
        'sucursales': sucursales,
        'comunas': comunas,
        'form': form,
    }
    return render(request, 'empresas/sucursales.html', context)

@require_POST
def crear_sucursal(request, empresa_id):
    """
    Crea una nueva sucursal para la empresa especificada.
    
    Valida los datos con SucursalForm y asigna la empresa y un usuario temporal.
    Retorna un JsonResponse para peticiones AJAX.
    """
    empresa = get_object_or_404(EmpEmpresas, id_empresa=empresa_id)
    form = SucursalForm(request.POST)
    if form.is_valid():
        try:
            with transaction.atomic():
                sucursal = form.save(commit=False)
                sucursal.id_empresa = empresa
                sucursal.id_usuario_id = 1  # Valor temporal
                sucursal.save()
            return JsonResponse({'success': True})
        except Exception as e:
            logger.error("Error creando sucursal: %s", e, exc_info=True)
            return JsonResponse({'success': False, 'error': 'Error interno'}, status=500)
    else:
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)

@require_http_methods(["GET", "POST"])
def actualizar_sucursal(request, id):
    """
    GET: Retorna los datos de una sucursal en formato JSON para cargar en el formulario de edición.
    POST: Actualiza los datos de la sucursal usando SucursalForm.
    """
    sucursal = get_object_or_404(EmpSucursales, id_sucursal=id)
    if request.method == "GET":
        data = {
            'id_sucursal': sucursal.id_sucursal,
            'nombre': sucursal.nombre,
            'direccion': sucursal.direccion,
            'latitud': sucursal.latitud,
            'longitud': sucursal.longitud,
            'id_comuna': sucursal.id_comuna_id,
        }
        return JsonResponse(data)
    else:  # POST
        form = SucursalForm(request.POST, instance=sucursal)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                return JsonResponse({'success': True})
            except Exception as e:
                logger.error("Error actualizando sucursal: %s", e, exc_info=True)
                return JsonResponse({'success': False, 'error': 'Error interno'}, status=500)
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

@require_POST
def eliminar_sucursal(request, id):
    """
    Elimina la sucursal identificada por 'id'.
    
    Retorna un JsonResponse indicando el éxito de la operación.
    """
    sucursal = get_object_or_404(EmpSucursales, id_sucursal=id)
    try:
        with transaction.atomic():
            sucursal.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error("Error eliminando sucursal: %s", e, exc_info=True)
        return JsonResponse({'success': False, 'error': 'Error interno'}, status=500)
def cargar_sucursal(request, id_sucursal):
    """
    Carga los detalles de una sucursal específica y los retorna en formato JSON.

    Args:
        id_sucursal (int): Identificador de la sucursal a cargar.

    Returns:
        JsonResponse: Datos de la sucursal o mensaje de error en caso de fallo.
    """
    try:
        sucursal = get_object_or_404(EmpSucursales, id_sucursal=id_sucursal)
        comuna = get_object_or_404(AdmComunas, id_comuna=sucursal.id_comuna_id)
        data = {
            'id_sucursal': sucursal.id_sucursal,
            'nombre': sucursal.nombre,
            'direccion': sucursal.direccion,
            'latitud': sucursal.latitud,
            'longitud': sucursal.longitud,
            'id_comuna': sucursal.id_comuna_id,
            'comuna_nombre': comuna.nombre,
            'id_usuario': 1,  # Hardcodeado temporalmente
           
        }
        return JsonResponse(data, status=200)
    except Exception as e:
        logger.error("Error loading sucursal details: %s", e, exc_info=True)
        return JsonResponse({'error': 'Error al cargar la sucursal.'}, status=500)


@require_POST
def guardar_red_apoyo(request, id_sucursal):
    """
    Guarda una nueva entrada en la red de apoyo para una sucursal.

    Recibe los datos vía POST, valida que el nombre esté presente y, si la operación es exitosa,
    retorna un JSON confirmando el éxito.

    Args:
        id_sucursal (int): Identificador de la sucursal a la que se asocia la red de apoyo.

    Returns:
        JsonResponse: Resultado de la operación con código de estado HTTP.
    """
    nombre = request.POST.get('nombre', '').strip()
    telefono = request.POST.get('telefono', '').strip()
    email = request.POST.get('email', '').strip()
    
    if not nombre:
        return JsonResponse({'success': False, 'error': 'El nombre es obligatorio'}, status=400)
    
    try:
        with transaction.atomic():
            nueva_red = EmpRedApoyo(
                id_sucursal_id=id_sucursal,
                nombre=nombre,
                telefono=telefono,
                email=email,
                id_usuario_id=1,  # Hardcodeado temporalmente
                fecha_registro=timezone.now()
            )
            nueva_red.save()
        return JsonResponse({'success': True}, status=200)
    except Exception as e:
        logger.error("Error al guardar red de apoyo: %s", e, exc_info=True)
        return JsonResponse({'success': False, 'error': 'Error interno. Intente nuevamente más tarde.'}, status=500)


def obtener_redes_apoyo(request, id_sucursal):
    """
    Obtiene y retorna la lista de redes de apoyo asociadas a una sucursal en formato JSON.

    Args:
        id_sucursal (int): Identificador de la sucursal.

    Returns:
        JsonResponse: Lista de redes de apoyo o mensaje de error en caso de fallo.
    """
    try:
        redes = EmpRedApoyo.objects.filter(id_sucursal=id_sucursal).values('id_nr', 'nombre', 'telefono', 'email')
        return JsonResponse({'redes': list(redes)}, status=200)
    except Exception as e:
        logger.error("Error obtaining redes de apoyo: %s", e, exc_info=True)
        return JsonResponse({'error': 'Error al obtener redes de apoyo.'}, status=500)


@require_POST
def eliminar_red_apoyo(request, id_nr):
    """
    Elimina una entrada de la red de apoyo identificada por id_nr.

    Args:
        id_nr (int): Identificador de la red de apoyo a eliminar.

    Returns:
        JsonResponse: Confirmación de eliminación o mensaje de error.
    """
    try:
        red = EmpRedApoyo.objects.get(id_nr=id_nr)
        with transaction.atomic():
            red.delete()
        return JsonResponse({'success': True}, status=200)
    except EmpRedApoyo.DoesNotExist:
        logger.error("Red de apoyo no encontrada: id_nr=%s", id_nr)
        return JsonResponse({'success': False, 'error': 'Red de apoyo no encontrada'}, status=404)
    except Exception as e:
        logger.error("Error eliminando red de apoyo: %s", e, exc_info=True)
        return JsonResponse({'success': False, 'error': 'Error interno al eliminar la red de apoyo.'}, status=500)
