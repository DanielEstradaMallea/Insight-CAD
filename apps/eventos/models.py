from django.db import models
from django.core.validators import FileExtensionValidator
from django.conf import settings



class EveTipos(models.Model):
    id_tipo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    activo = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'eve_tipos'

class EveSubtipos(models.Model):
    id_subtipo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    id_tipo = models.ForeignKey(EveTipos, models.DO_NOTHING, db_column='id_tipo')
    prioridad = models.CharField(max_length=20)
    alerta_encendida = models.CharField(max_length=2)
    detalle = models.CharField(max_length=255, blank=True, null=True)
    activo = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'eve_subtipos'

class EveProcedencias(models.Model):
    id_procedencia = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    activo = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'eve_procedencias'

class EveAtributosSubtipos(models.Model):
    id_atributo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    id_subtipo = models.ForeignKey(EveSubtipos, models.DO_NOTHING, db_column='id_subtipo')
    tipo_valor = models.CharField(max_length=20)
    obligatorio = models.CharField(max_length=2)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    activo = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'eve_atributos_subtipos'

class EveValoresListas(models.Model):
    id_valor_lista = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    id_atributo = models.ForeignKey(EveAtributosSubtipos, models.DO_NOTHING, db_column='id_atributo')
    activo = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'eve_valores_listas'



class EveAtributosEventos(models.Model):
    id_atributo = models.IntegerField(primary_key=True)  # The composite primary key (id_atributo, id_evento) found, that is not supported. The first column is selected.
    id_evento = models.IntegerField()
    valor_numerico = models.FloatField(blank=True, null=True)
    valor_texto = models.TextField(blank=True, null=True)
    id_valor_lista = models.ForeignKey(EveValoresListas, models.DO_NOTHING, db_column='id_valor_lista', blank=True, null=True)
    valor_fecha = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'eve_atributos_eventos'
        unique_together = (('id_atributo', 'id_evento'),)





class EveEstados(models.Model):
    id_estado = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    activo = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'eve_estados'

class EveEventos(models.Model):
    id_evento = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    tipo_evento = models.CharField(max_length=20)
    id_tipo = models.ForeignKey(EveTipos, models.DO_NOTHING, db_column='id_tipo')
    id_subtipo = models.ForeignKey(EveSubtipos, models.DO_NOTHING, db_column='id_subtipo')
    id_procedencia = models.ForeignKey(EveProcedencias, models.DO_NOTHING, db_column='id_procedencia')
    fecha = models.DateField()
    hora = models.TimeField()
    direccion = models.CharField(max_length=500)
    latitud = models.CharField(max_length=30)
    longitud = models.CharField(max_length=30)
    id_comuna = models.ForeignKey('mantenedores.AdmComunas', models.DO_NOTHING, db_column='id_comuna', blank=True, null=True)
    detalle = models.TextField(blank=True, null=True)
    id_sucursal = models.ForeignKey('empresas.EmpSucursales', models.DO_NOTHING, db_column='id_sucursal', blank=True, null=True)
    id_dispositivo = models.ForeignKey('dispositivos.DisDispositivos', models.DO_NOTHING, db_column='id_dispositivo', blank=True, null=True)
    id_sensor = models.ForeignKey('dispositivos.DisSensores', models.DO_NOTHING, db_column='id_sensor', blank=True, null=True)
    id_estado_actual = models.ForeignKey(EveEstados, models.DO_NOTHING, db_column='id_estado_actual', blank=True, null=True)
    alerta_encendida = models.CharField(max_length=2, choices=[('SI', 'SI'), ('NO', 'NO')], default='SI')
    fecha_alerta = models.DateTimeField(blank=True, null=True)
    observaciones_cierre = models.TextField(blank=True, null=True)
    id_usuario = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.DO_NOTHING,db_column='id_usuario',blank=True, null=True, related_name='eventos_creados')
    fecha_registro = models.DateTimeField(blank=True, null=True)
    procesado_ia = models.CharField(max_length=2, blank=True, null=True)
    procesado_ia_fecha = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'eve_eventos'
        
        
class EveEstadosEventos(models.Model):
    id_nr = models.AutoField(primary_key=True)
    id_evento = models.ForeignKey(EveEventos, models.DO_NOTHING, db_column='id_evento')
    id_estado = models.ForeignKey(EveEstados, models.DO_NOTHING, db_column='id_estado')
    id_usuario = models.ForeignKey('personas.Usuarios', models.DO_NOTHING, db_column='id_usuario')
    fecha_registro = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'eve_estados_eventos'


class EveAntecedentesEventos(models.Model):
    id_antecedente = models.AutoField(primary_key=True)
    id_evento = models.ForeignKey(EveEventos, models.DO_NOTHING, db_column='id_evento')
    antecedente = models.TextField()
    fecha = models.DateField()
    hora = models.TimeField()
    id_usuario = models.ForeignKey('personas.Usuarios', models.DO_NOTHING, db_column='id_usuario')
    fecha_registro = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'eve_antecedentes_eventos'
        
class EveDocumentosEventos(models.Model):
    id_documento = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, blank=True, null=True)
    id_evento = models.ForeignKey(EveEventos, models.DO_NOTHING, db_column='id_evento')
    nombre_archivo = models.CharField(max_length=50)
    fecha_registro = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'eve_documentos_eventos'
        

class EveImagenesEventos(models.Model):
    id_imagen = models.AutoField(primary_key=True)
    id_evento = models.ForeignKey(
        'EveEventos', 
        on_delete=models.CASCADE,  # Elimina las imágenes si se borra el evento
        db_column='id_evento',
        related_name='imagenes'  # Acceso desde EveEventos: evento.imagenes.all()
    )
    nombre = models.CharField(max_length=100, blank=True, null=True)
    archivo = models.ImageField(
        upload_to='eventos/imagenes/',  # Subdirectorio dentro de MEDIA_ROOT
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])]
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)  # Fecha automática

    class Meta:
        managed = False
        db_table = 'eve_imagenes_eventos'

    def __str__(self):
        return f"Imagen {self.id_imagen} - {self.id_evento.nombre}"