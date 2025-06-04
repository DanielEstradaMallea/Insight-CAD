from django.db import models

class DisCompaniasSim(models.Model):
    id_compania_sim = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    activo = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'dis_companias_sim'



class DisTiposDispositivos(models.Model):
    id_tipo_dispositivo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    activo = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'dis_tipos_dispositivos'


class DisTiposSensores(models.Model):
    id_tipo_sensor = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    activo = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'dis_tipos_sensores'


class DisTiposSim(models.Model):
    id_tipo_sim = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    activo = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'dis_tipos_sim'

class DisDispositivos(models.Model):
    id_dispositivo = models.AutoField(primary_key=True)
    numero_serie = models.CharField(max_length=255)
    id_tipo_dispositivo = models.ForeignKey(DisTiposDispositivos, models.DO_NOTHING, db_column='id_tipo_dispositivo')
    telefono = models.CharField(max_length=20)
    id_compania_sim = models.ForeignKey(DisCompaniasSim, models.DO_NOTHING, db_column='id_compania_sim', blank=True, null=True)
    id_tipo_sim = models.ForeignKey(DisTiposSim, models.DO_NOTHING, db_column='id_tipo_sim', blank=True, null=True)
    endpoint1 = models.CharField(max_length=255, blank=True, null=True)
    endpoint2 = models.CharField(max_length=255, blank=True, null=True)
    id_sucursal = models.ForeignKey('empresas.EmpSucursales', models.DO_NOTHING, db_column='id_sucursal', blank=True, null=True)
    ubicacion = models.CharField(max_length=100)
    latitud = models.CharField(max_length=30)
    longitud = models.CharField(max_length=30)
    habilitado = models.CharField(max_length=2)
    id_usuario = models.ForeignKey('personas.Usuarios', models.DO_NOTHING, db_column='id_usuario')
    fecha_registro = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'dis_dispositivos'

class DisSensores(models.Model):
    id_sensor = models.AutoField(primary_key=True)
    codigo_unico = models.CharField(unique=True, max_length=20)
    id_dispositivo = models.ForeignKey(DisDispositivos, models.DO_NOTHING, db_column='id_dispositivo')
    id_tipo_sensor = models.ForeignKey(DisTiposSensores, models.DO_NOTHING, db_column='id_tipo_sensor')
    ubicacion = models.CharField(max_length=255)
    habilitado = models.CharField(max_length=2)
    id_usuario = models.ForeignKey('personas.Usuarios', models.DO_NOTHING, db_column='id_usuario')
    fecha_registro = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'dis_sensores'
