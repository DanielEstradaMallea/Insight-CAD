from django.http import JsonResponse
from apps.eventos.models import EveEventos
from django.shortcuts import render
from math import isnan


def mostrar_mapa(request):
    return render(request, 'mapas/mapa.html')  # Archivo template que contiene el mapa

def mostrar_mapa_gps(request):
    return render(request, 'mapas/mapagps.html')

def mostrar_mapa_calor(request):
    return render(request, 'mapas/mapacalor.html')

#trae los reportes que tienen alerta encendida

def obtener_eventos(request):
    eventos = EveEventos.objects.filter(alerta_encendida='SI').select_related(
        'id_tipo', 'id_subtipo', 'id_comuna'
    ).values(
        'id_evento', 
        'nombre', 
        'latitud', 
        'longitud', 
        'detalle', 
        'fecha_alerta',
        'id_tipo__nombre', 
        'id_subtipo__nombre', 
        'id_comuna__nombre', 
        'id_subtipo__prioridad',
        'alerta_encendida',
        'fecha',
        'hora', 
    )

    # Filtrar eventos con coordenadas válidas
    eventos_validos = []
    for evento in eventos:
        try:
            lat = float(evento['latitud'])
            lng = float(evento['longitud'])
            if not (isnan(lat) or isnan(lng)):  # Verificar que no sean NaN
                # Convertir la prioridad a un valor numérico
                prioridad = evento['id_subtipo__prioridad']
                if prioridad == 'BAJA':
                    evento['peso'] = 1
                elif prioridad == 'MEDIA':
                    evento['peso'] = 2
                elif prioridad == 'ALTA':
                    evento['peso'] = 3
                else:
                    evento['peso'] = 0  # Valor por defecto
                eventos_validos.append(evento)
        except (ValueError, TypeError):
            continue  # Ignorar eventos con coordenadas inválidas

    return JsonResponse(eventos_validos, safe=False)



def infoscan_mapa(request):
    return render(request, 'mapas/infoscan.html')  # Archivo template que contiene el mapa

def infoscan_eventos(request):
    # Filtrar eventos con alerta encendida y traer datos relacionados
    eventos = EveEventos.objects.all().select_related(
        'id_tipo', 'id_subtipo', 'id_comuna'
    ).values(
        'id_evento', 
        'nombre', 
        'latitud', 
        'longitud', 
        'detalle', 
        'fecha_alerta',
        'hora', 
        'id_tipo__nombre',       
        'id_subtipo__nombre',     
        'id_comuna__nombre',       
        'id_subtipo__prioridad',
        'fecha'
    )
    return JsonResponse(list(eventos), safe=False)


def mapa_calor_eventos(request):
    eventos = EveEventos.objects.select_related('id_subtipo').all().values(
        'latitud', 'longitud', 'id_subtipo__prioridad'
    )
    
    eventos_data = []
    for evento in eventos:
        lat = evento['latitud']
        lng = evento['longitud']
        prioridad = evento['id_subtipo__prioridad']
        
        eventos_data.append({
            'latitud': lat,
            'longitud': lng,
            'prioridad': prioridad
        })
    
    return JsonResponse(eventos_data, safe=False)

from apps.eventos.models import EveEventos, EveSubtipos, EveProcedencias
from apps.empresas.models import EmpEmpresas, EmpSucursales
from datetime import datetime, date
import json, io, openpyxl
from django.http      import JsonResponse, HttpResponse


def mapa_eventos(request):
    """Renderiza el mapa con filtros."""
    context = {
        'subtipos':     EveSubtipos.objects.all(),
        'procedencias': EveProcedencias.objects.all(),
        'empresas':     EmpEmpresas.objects.all(),
        'sucursales':   EmpSucursales.objects.all(),
        'today':        date.today().strftime('%Y-%m-%d'),
    }
    return render(request, 'mapas/mapa_eventos.html', context)


def api_eventos(request):
    today = date.today()
    default_start = today - timedelta(days=365)
    fi = request.GET.get('fecha_inicio', default_start.strftime('%Y-%m-%d'))
    ff = request.GET.get('fecha_fin', today.strftime('%Y-%m-%d'))
    st = request.GET.getlist('subtipo[]', [])
    pr = request.GET.getlist('prioridad[]', [])
    pc = request.GET.get('procedencia', 'all')
    em = request.GET.get('empresa', 'all')
    su = request.GET.get('sucursal', 'all')

    filtros = Q(fecha__range=[fi, ff])
    if st and 'all' not in st:
        filtros &= Q(id_subtipo__in=st)
    if pr and 'all' not in pr:
        filtros &= Q(id_subtipo__prioridad__in=pr)
    if pc != 'all':
        filtros &= Q(id_procedencia=pc)
    if em != 'all':
        filtros &= Q(id_sucursal__id_empresa=em)
    if su != 'all':
        filtros &= Q(id_sucursal=su)

    eventos = EveEventos.objects.filter(filtros).select_related('id_tipo', 'id_subtipo').values(
        'id_evento', 'nombre', 'latitud', 'longitud', 'fecha', 'hora',
        'id_tipo__nombre', 'id_subtipo__nombre', 'id_subtipo__prioridad'
    )

    data = []
    for e in eventos:
        try:
            lat = float(e['latitud'])
            lng = float(e['longitud'])
        except Exception:
            continue
        data.append({
            'id': e['id_evento'],
            'nombre': e['nombre'],
            'tipo': e['id_tipo__nombre'],
            'subtipo': e['id_subtipo__nombre'],
            'prioridad': e['id_subtipo__prioridad'],
            'fecha': e['fecha'].strftime('%Y-%m-%d'),
            'hora': e['hora'].strftime('%H:%M:%S'),
            'lat': lat,
            'lng': lng,
        })
    return JsonResponse({'eventos': data})

  
def export_cluster_excel(request):
    """Exporta a Excel los eventos seleccionados."""
    payload = json.loads(request.body)
    eventos = payload.get('eventos', [])

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["ID", "Nombre", "Tipo", "Fecha", "Hora", "Lat", "Lng"])
    for ev in eventos:
        ws.append([ev['id'], ev['nombre'], ev['tipo'], ev['fecha'], ev['hora'], ev['lat'], ev['lng']])

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)

    response = HttpResponse(
        stream.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="cluster_eventos.xlsx"'
    return response


from django.http import JsonResponse
from django.utils.timezone import localdate
from django.db.models import Count, Q
from django.db.models.functions import ExtractHour
from apps.eventos.models import EveEventos, EveEstados
from datetime import date, timedelta

def dashboard_eventos_data(request):
    # Filtros GET
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    id_comuna = request.GET.get('id_comuna')

    # Rango de fechas por defecto: últimos 90 días
    hoy = date.today()
    dias = 90
    if fecha_inicio and fecha_fin:
        try:
            fecha_inicio = date.fromisoformat(fecha_inicio)
            fecha_fin = date.fromisoformat(fecha_fin)
        except Exception:
            fecha_fin = hoy
            fecha_inicio = hoy - timedelta(days=dias-1)
    else:
        fecha_fin = hoy
        fecha_inicio = hoy - timedelta(days=dias-1)

    filtros = Q(fecha__range=(fecha_inicio, fecha_fin))
    if id_comuna:
        filtros &= Q(id_comuna_id=id_comuna)

    # Eventos totales hoy
    eventos_hoy = EveEventos.objects.filter(fecha=hoy).filter(filtros).count()
    # Eventos alta prioridad hoy
    eventos_alta = EveEventos.objects.filter(fecha=hoy, id_subtipo__prioridad='ALTA').filter(filtros).count()
    # Eventos este mes (solo desde el 1er día)
    eventos_mes = EveEventos.objects.filter(
        fecha__gte=hoy.replace(day=1)
    ).filter(filtros).count()

    # 🚨 Eventos con alerta activa (alerta_encendida="SI")
    eventos_alerta_activa = EveEventos.objects.filter(filtros, alerta_encendida="SI").count()

    # Prioridad agregada (BAJA, MEDIA, ALTA)
    prioridad_qs = EveEventos.objects.filter(filtros).values('id_subtipo__prioridad').annotate(total=Count('id_evento'))
    prioridad = {"BAJA": 0, "MEDIA": 0, "ALTA": 0}
    for row in prioridad_qs:
        prio = row['id_subtipo__prioridad']
        if prio in prioridad:
            prioridad[prio] = row['total']

    # Por tipo de evento
    tipo_qs = EveEventos.objects.filter(filtros).values('id_tipo__nombre').annotate(total=Count('id_evento'))
    tipo = {row['id_tipo__nombre']: row['total'] for row in tipo_qs}

    # Gráfico de línea: eventos por día y prioridad
    fechas = [fecha_inicio + timedelta(days=i) for i in range((fecha_fin-fecha_inicio).days+1)]
    data_dias = {str(f): {"BAJA": 0, "MEDIA": 0, "ALTA": 0} for f in fechas}
    eventos_por_dia = EveEventos.objects.filter(filtros).values('fecha', 'id_subtipo__prioridad').annotate(total=Count('id_evento'))
    for row in eventos_por_dia:
        fecha = str(row['fecha'])
        prioridad_ev = row['id_subtipo__prioridad']
        if fecha in data_dias and prioridad_ev in data_dias[fecha]:
            data_dias[fecha][prioridad_ev] = row['total']

    lineaDias = [
        {
            "dia": f.strftime("%Y-%m-%d"),
            "baja": data_dias[str(f)]["BAJA"],
            "media": data_dias[str(f)]["MEDIA"],
            "alta": data_dias[str(f)]["ALTA"]
        }
        for f in fechas
    ]

    # Radar (modifica según tus reglas)
    radar = {
        "Eventos Cerrados": EveEventos.objects.filter(id_estado_actual__nombre="FINALIZADO").filter(filtros).count(),
        "Eventos Abiertos": EveEventos.objects.filter(id_estado_actual__nombre="ABIERTO").filter(filtros).count(),
        "En Proceso": EveEventos.objects.filter(id_estado_actual__nombre="EN PROCESO").filter(filtros).count(),
        "Ingresado": EveEventos.objects.filter(id_estado_actual__nombre="INGRESADO").filter(filtros).count(),
    }

    # Gráfico de eventos por hora usando ExtractHour sobre campo 'hora'
    qs_horas = (
        EveEventos.objects
        .filter(filtros)
        .annotate(hora_ev=ExtractHour('hora'))  # hora_ev será un int entre 0-23
        .values('hora_ev')
        .annotate(total=Count('id_evento'))
    )
    eventos_por_hora = [0] * 24
    for row in qs_horas:
        h = row['hora_ev']
        if h is not None and 0 <= h < 24:
            eventos_por_hora[h] = row['total']

    # Armado del JSON final
    data = {
        "hoy": eventos_hoy,
        "alta": eventos_alta,
        "mes": eventos_mes,
        "alerta_activa": eventos_alerta_activa,
        "prioridad": prioridad,
        "tipo": tipo,
        "lineaDias": lineaDias,
        "radar": radar,
        "eventosPorHora": eventos_por_hora,
        "fecha_inicio": fecha_inicio.strftime("%Y-%m-%d"),
        "fecha_fin": fecha_fin.strftime("%Y-%m-%d"),
    }
    return JsonResponse(data)




from apps.eventos.models import EveTipos, EveSubtipos
from apps.mantenedores.models import AdmComunas

def dashboard_view(request):
    comunas = AdmComunas.objects.all().order_by('nombre')
    tipos = EveTipos.objects.all().order_by('nombre')
    subtipos = EveSubtipos.objects.all().order_by('nombre')
    return render(request, "mapas/dashboard.html", {
        "comunas": comunas,
        "tipos": tipos,
        "subtipos": subtipos
    })