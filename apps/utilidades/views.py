from django.views.decorators.http import require_POST, require_GET
from django.http import HttpResponse
from .models import EvePersonasEventos, EveVehiculosEventos, EvePersonasEventosPK
from apps.personas.models import PerPersonas, EveTiposPersonas
from apps.vehiculos.models import VehVehiculos
from apps.eventos.models import EveEventos
from django.shortcuts import render, get_object_or_404
import json
from django.http import JsonResponse
from django.db.models import Q
from datetime import datetime
from django.db import connection



########################################################################################################
##### Asignacion de vehiculos al evento

@require_POST
def registrar_persona_evento(request):
    try:
        # Obtener los datos JSON enviados en el cuerpo de la solicitud
        data = json.loads(request.body)
        persona_id = data.get('persona_id')
        tipo_persona_id = data.get('tipo_persona_id')
        evento_id = data.get('evento_id')

        # Verificar si ya existe la relación (persona-evento)
        if not EvePersonasEventos.objects.filter(
            id_persona=persona_id,
            id_evento=evento_id
        ).exists():
            # Crear el registro en la tabla de apoyo (EvePersonasEventos)
            EvePersonasEventos.objects.create(
                id_persona=persona_id,  # No se usa '_id' porque no es una clave foránea
                id_evento=evento_id,
                id_tipo_persona=tipo_persona_id  # Igualmente, no se usa '_id' aquí
            )
            return JsonResponse({'success': True})

        else:
            return JsonResponse({'success': False, 'error': 'La persona ya está registrada en este evento'})
    
    except Exception as e:
        # Capturar cualquier error y devolverlo en una respuesta JSON
        return JsonResponse({'success': False, 'error': str(e)})

@require_GET
def obtener_personas_evento(request):
    evento_id = request.GET.get('evento_id')
    
    if not evento_id:
        return JsonResponse({'success': False, 'error': 'Falta el ID del evento'}, status=400)

    # Obtener las filas de personas asociadas al evento
    personas_evento = EvePersonasEventos.objects.filter(id_evento=evento_id).values(
        'id_persona', 'id_tipo_persona')

    # Obtener los datos de persona y tipo de persona con consultas adicionales
    resultado = []
    for persona_evento in personas_evento:
        try:
            persona = PerPersonas.objects.get(id_persona=persona_evento['id_persona'])
            tipo_persona = EveTiposPersonas.objects.get(id_tipo_persona=persona_evento['id_tipo_persona'])

            resultado.append({
                'id_persona': persona.id_persona,  # Se cambia 'id' por 'id_persona'
                'rut': persona.rut,
                'nombre': persona.nombre,
                'tipo_persona': tipo_persona.nombre
            })
        except (PerPersonas.DoesNotExist, EveTiposPersonas.DoesNotExist):
            continue  # Si no encuentra el dato, simplemente lo omite

    return JsonResponse({'success': True, 'data': resultado})






########################################################################################################
##### Asignacion de vehiculos al evento

@require_POST
def registrar_vehiculo_evento(request):
    try:
        # Obtener los datos JSON enviados en el cuerpo de la solicitud
        data = json.loads(request.body)
        vehiculo_id = data.get('vehiculo_id')
        evento_id = data.get('evento_id')

        # Verificar si ya existe la relación (vehículo-evento)
        if not EveVehiculosEventos.objects.filter(
            id_vehiculo=vehiculo_id,
            id_evento=evento_id
        ).exists():
            # Crear el registro en la tabla de apoyo (EveVehiculosEventos)
            EveVehiculosEventos.objects.create(
                id_vehiculo=vehiculo_id,
                id_evento=evento_id
            )
            return JsonResponse({'success': True})

        else:
            return JsonResponse({'success': False, 'error': 'El vehículo ya está registrado en este evento'})
    
    except Exception as e:
        # Capturar cualquier error y devolverlo en una respuesta JSON
        return JsonResponse({'success': False, 'error': str(e)})
    
    
@require_GET
def obtener_vehiculos_evento(request):
    evento_id = request.GET.get('evento_id')
    
    if not evento_id:
        return JsonResponse({'success': False, 'error': 'Falta el ID del evento'}, status=400)

    # Obtener las filas de vehículos asociadas al evento
    vehiculos_evento = EveVehiculosEventos.objects.filter(id_evento=evento_id).values('id_vehiculo')

    # Obtener los datos de vehículo con consultas adicionales
    resultado = []
    for vehiculo_evento in vehiculos_evento:
        try:
            vehiculo = VehVehiculos.objects.get(id_vehiculo=vehiculo_evento['id_vehiculo'])
            marca = vehiculo.id_marca_vehiculo.nombre if vehiculo.id_marca_vehiculo else None
            tipo = vehiculo.id_tipo_vehiculo.nombre if vehiculo.id_tipo_vehiculo else None

            resultado.append({
                'id_vehiculo': vehiculo.id_vehiculo,
                'patente': vehiculo.patente,
                'marca': marca,
                'modelo': vehiculo.modelo,
                'tipo': tipo
            })
        except VehVehiculos.DoesNotExist:
            continue  # Si no encuentra el dato, simplemente lo omite

    return JsonResponse({'success': True, 'data': resultado})

#################
### busqueda personas reporte

def buscar_persona(request):
    # Se obtienen los parámetros de búsqueda
    rut = request.GET.get('rut', '').strip()
    nombre = request.GET.get('nombre', '').strip()
    persons = []

    # Si se ingresa RUT se realiza la búsqueda por este criterio; de lo contrario, se busca por nombre o apellido.
    if rut:
        persons = PerPersonas.objects.filter(rut__icontains=rut)
    elif nombre:
        persons = PerPersonas.objects.filter(
            Q(nombre__icontains=nombre) | Q(paterno__icontains=nombre) | Q(materno__icontains=nombre)
        )
    
    context = {
        'persons': persons,
        'rut': rut,
        'nombre': nombre,
    }
    return render(request, 'reportes/buscar_persona.html', context)


def get_eventos_data(persona_id, fecha_inicio, fecha_fin):
    date_condition = ""
    params = [persona_id]  # Primer parámetro: id_persona

    if fecha_inicio and fecha_fin:
        try:
            inicio_date = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fin_date = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            date_condition = " AND e.fecha BETWEEN %s AND %s"
            params.extend([inicio_date, fin_date])
        except ValueError:
            pass  # Si las fechas no son válidas, se ignora el filtro

    query = f"""
        SELECT 
    e.id_evento, 
    e.nombre AS evento,
    t.nombre AS tipo_evento,  -- se obtiene el nombre real desde la tabla de tipos
    st.nombre AS subtipo_evento,
    e.fecha, 
    e.hora, 
    e.direccion, 
    tp.nombre AS tipo_persona
FROM eve_eventos e
JOIN eve_personas_eventos pe ON e.id_evento = pe.id_evento
JOIN eve_tipos_personas tp ON pe.id_tipo_persona = tp.id_tipo_persona
JOIN eve_subtipos st ON e.id_subtipo = st.id_subtipo
JOIN eve_tipos t ON e.id_tipo = t.id_tipo  -- se une la tabla de tipos
WHERE pe.id_persona = %s {date_condition}
ORDER BY e.fecha DESC, e.hora DESC
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return data


def eventos_persona(request):
    persona_id = request.GET.get('persona_id')
    if not persona_id:
        return HttpResponse("No se seleccionó persona.", status=400)
    
    persona = get_object_or_404(PerPersonas, id_persona=persona_id)
    
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    
    eventos = get_eventos_data(persona_id, fecha_inicio, fecha_fin)
    
    context = {
        'persona': persona,
        'eventos': eventos,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }
    return render(request, 'reportes/eventos_persona.html', context)

import openpyxl

def export_eventos_excel(request):
    persona_id = request.GET.get('persona_id')
    if not persona_id:
        return HttpResponse("No se seleccionó persona.", status=400)
    
    persona = PerPersonas.objects.filter(id_persona=persona_id).first()
    
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    
    eventos = get_eventos_data(persona_id, fecha_inicio, fecha_fin)
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Eventos"
    
    # Encabezado según el orden solicitado
    header = ["ID", "Evento", "Tipo Evento", "Subtipo Evento", "Fecha", "Hora", "Dirección", "Tipo de Asociación"]
    ws.append(header)
    
    for evento in eventos:
        row = [
            evento.get("id_evento"),
            evento.get("evento"),
            evento.get("tipo_evento"),
            evento.get("subtipo_evento"),
            evento.get("fecha"),
            evento.get("hora"),
            evento.get("direccion"),
            evento.get("tipo_persona"),
        ]
        ws.append(row)
    
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="eventos.xlsx"'
    wb.save(response)
    return response

#############################
# Reporte de vehiculos

def buscar_vehiculo(request):
    patente = request.GET.get('patente', '').strip()
    modelo = request.GET.get('modelo', '').strip()
    vehicles = []
    
    if patente:
        vehicles = VehVehiculos.objects.filter(patente__icontains=patente)
    elif modelo:
        vehicles = VehVehiculos.objects.filter(modelo__icontains=modelo)
    
    context = {
        'vehicles': vehicles,
        'patente': patente,
        'modelo': modelo,
    }
    return render(request, 'reportes/buscar_vehiculo.html', context)

def eventos_vehiculo(request):
    vehiculo_id = request.GET.get('vehiculo_id')
    if not vehiculo_id:
        return HttpResponse("No se seleccionó vehículo.", status=400)
    
    # Obtener el vehículo seleccionado
    vehicle = get_object_or_404(VehVehiculos, id_vehiculo=vehiculo_id)
    
    # Obtener el rango de fechas, si se especificó
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    date_condition = ""
    params = [vehiculo_id]  # Primer parámetro: id_vehiculo

    if fecha_inicio and fecha_fin:
        try:
            inicio_date = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fin_date = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            date_condition = " AND e.fecha BETWEEN %s AND %s"
            params.extend([inicio_date, fin_date])
        except ValueError:
            pass

    # Consulta RAW para unir eventos, la relación de vehículos y subtipos
    query = f"""
        SELECT 
            e.id_evento,
            e.nombre AS evento,
            e.tipo_evento,
            st.nombre AS subtipo_evento,
            e.fecha,
            e.hora,
            e.direccion
        FROM eve_eventos e
        JOIN eve_vehiculos_eventos ve ON e.id_evento = ve.id_evento
        JOIN eve_subtipos st ON e.id_subtipo = st.id_subtipo
        WHERE ve.id_vehiculo = %s {date_condition}
        ORDER BY e.fecha DESC, e.hora DESC
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        eventos_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    context = {
        'vehicle': vehicle,
        'eventos': eventos_list,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }
    return render(request, 'reportes/eventos_vehiculo.html', context)

def export_vehiculos_excel(request):
    vehiculo_id = request.GET.get('vehiculo_id')
    if not vehiculo_id:
        return HttpResponse("No se seleccionó vehículo.", status=400)
    
    # Obtener el vehículo para usar datos en el Excel (opcional)
    vehicle = get_object_or_404(VehVehiculos, id_vehiculo=vehiculo_id)
    
    # Obtener rango de fechas
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    date_condition = ""
    params = [vehiculo_id]  # El primer parámetro es la identificación del vehículo

    if fecha_inicio and fecha_fin:
        try:
            inicio_date = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fin_date = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            date_condition = " AND e.fecha BETWEEN %s AND %s"
            params.extend([inicio_date, fin_date])
        except ValueError:
            pass  # Si las fechas no son válidas, se ignora el filtro

    # Consulta RAW que une la tabla de eventos, la de relación de vehículos y subtipos
    query = f"""
        SELECT 
            e.id_evento,
            e.nombre AS evento,
            e.tipo_evento,
            st.nombre AS subtipo_evento,
            e.fecha,
            e.hora,
            e.direccion
        FROM eve_eventos e
        JOIN eve_vehiculos_eventos ve ON e.id_evento = ve.id_evento
        JOIN eve_subtipos st ON e.id_subtipo = st.id_subtipo
        WHERE ve.id_vehiculo = %s {date_condition}
        ORDER BY e.fecha DESC, e.hora DESC
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        eventos_list = [dict(zip(columns, row)) for row in cursor.fetchall()]

    # Crear el libro Excel usando openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Eventos Vehículo"

    # Encabezado (puedes agregar datos del vehículo si lo deseas)
    header = ["ID", "Evento", "Tipo Evento", "Subtipo Evento", "Fecha", "Hora", "Dirección"]
    ws.append(header)

    # Escribir cada fila con los datos de los eventos
    for evento in eventos_list:
        row = [
            evento.get("id_evento"),
            evento.get("evento"),
            evento.get("tipo_evento"),
            evento.get("subtipo_evento"),
            evento.get("fecha"),
            evento.get("hora"),
            evento.get("direccion"),
        ]
        ws.append(row)

    # Preparar la respuesta para descarga del archivo Excel
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    filename = "eventos_vehiculo.xlsx"
    response["Content-Disposition"] = f"attachment; filename={filename}"
    wb.save(response)
    return response