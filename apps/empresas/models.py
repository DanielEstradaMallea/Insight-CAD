from django.db import models
from django.utils import timezone



class EmpEmpresas(models.Model):
    id_empresa = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=120)
    rut = models.CharField(max_length=20, blank=True, null=True)
    nombre_representante = models.CharField(max_length=120, blank=True, null=True)
    telefono_representante = models.CharField(max_length=20, blank=True, null=True)
    email_representante = models.CharField(max_length=60, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    activo = models.CharField(max_length=2)
    id_usuario = models.ForeignKey('personas.Usuarios', models.DO_NOTHING, db_column='id_usuario')
    fecha_registro = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'emp_empresas'

class EmpSucursales(models.Model):
    id_sucursal = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=120)
    id_empresa = models.ForeignKey(EmpEmpresas, models.DO_NOTHING, db_column='id_empresa')
    direccion = models.CharField(max_length=120)
    latitud = models.CharField(max_length=30)
    longitud = models.CharField(max_length=30)
    id_comuna = models.ForeignKey('mantenedores.AdmComunas', models.DO_NOTHING, db_column='id_comuna', blank=True, null=True)
    id_usuario = models.ForeignKey('personas.Usuarios', models.DO_NOTHING, db_column='id_usuario')
    fecha_registro = models.DateTimeField(default=timezone.now)


    class Meta:
        managed = False
        db_table = 'emp_sucursales'


class EmpRedApoyo(models.Model):
    id_nr = models.AutoField(primary_key=True)
    id_sucursal = models.ForeignKey(EmpSucursales, models.DO_NOTHING, db_column='id_sucursal')
    nombre = models.CharField(max_length=120)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=60, blank=True, null=True)
    id_usuario = models.ForeignKey('personas.Usuarios', models.DO_NOTHING, db_column='id_usuario')
    fecha_registro = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'emp_red_apoyo'


