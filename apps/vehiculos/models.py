from django.db import models
from apps.eventos.models import EveEventos

class VehMarcasVehiculos(models.Model):
    id_marca_vehiculo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=60)
    activo = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'veh_marcas_vehiculos'


class VehTiposVehiculos(models.Model):
    id_tipo_vehiculo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=60)
    activo = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'veh_tipos_vehiculos'


class VehVehiculos(models.Model):
    id_vehiculo = models.AutoField(primary_key=True)
    patente = models.CharField(unique=True, max_length=10)
    id_marca_vehiculo = models.ForeignKey(VehMarcasVehiculos, models.DO_NOTHING, db_column='id_marca_vehiculo', blank=True, null=True)
    modelo = models.CharField(max_length=60, blank=True, null=True)
    color = models.CharField(max_length=60, blank=True, null=True)
    id_tipo_vehiculo = models.ForeignKey(VehTiposVehiculos, models.DO_NOTHING, db_column='id_tipo_vehiculo', blank=True, null=True)
    lista_gris = models.CharField(max_length=2)
    activo = models.CharField(max_length=2)
    id_usuario = models.ForeignKey('personas.Usuarios', models.DO_NOTHING, db_column='id_usuario')
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'veh_vehiculos'


class VehVehiculosGrises(models.Model):
    id_nr = models.AutoField(primary_key=True)
    id_vehiculo = models.IntegerField()
    accion = models.CharField(max_length=10)
    id_usuario = models.IntegerField()
    fecha_registro = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'veh_vehiculos_grises'
        
class Cuadrilla(models.Model):
    nombre = models.CharField(max_length=100)
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)
    ESTADOS = (
        ('disponible', 'Disponible'),
        ('en_camino', 'En Camino'),
    )
    estado = models.CharField(max_length=20, choices=ESTADOS, default='disponible')

    def __str__(self):
        return self.nombre

class Asignacion(models.Model):
    evento = models.ForeignKey(EveEventos, on_delete=models.CASCADE)
    cuadrilla = models.ForeignKey(Cuadrilla, on_delete=models.CASCADE)
    # Aquí podrías almacenar el recorrido (ruta) en formato JSON (lista de coordenadas)
    ruta = models.JSONField(blank=True, null=True)
    ESTADOS = (
        ('asignado', 'Asignado'),
        ('cancelado', 'Cancelado'),
        ('completado', 'Completado'),
    )
    estado = models.CharField(max_length=20, choices=ESTADOS, default='asignado')
    asignado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.evento.nombre} - {self.cuadrilla.nombre} ({self.estado})"
