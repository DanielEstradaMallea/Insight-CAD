from django.db import models
from apps.mantenedores import models as mantenedor
from apps.utilidades import models as utilidades
from django.utils import timezone

class PerPersonas(models.Model):
    id_persona = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=60)
    paterno = models.CharField(max_length=60)
    materno = models.CharField(max_length=60, blank=True, null=True)
    rut = models.CharField(unique=True, max_length=20)
    id_pais = models.ForeignKey(mantenedor.AdmPaises, models.DO_NOTHING, db_column='id_pais', blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    id_genero = models.ForeignKey(mantenedor.AdmGenero, models.DO_NOTHING, db_column='id_genero')
    id_estado_civil = models.ForeignKey(mantenedor.AdmEstadosCiviles, models.DO_NOTHING, db_column='id_estado_civil', blank=True, null=True)
    direccion = models.CharField(max_length=120, blank=True, null=True)
    id_comuna = models.ForeignKey(mantenedor.AdmComunas, models.DO_NOTHING, db_column='id_comuna', blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=60, blank=True, null=True)
    lista_gris = models.CharField(max_length=2)
    id_usuario = models.ForeignKey('Usuarios', models.DO_NOTHING, db_column='id_usuario',blank=True, null=True)
    fecha_registro = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'per_personas'
    def __str__(self):
        return f"{self.nombre} {self.paterno} {self.materno or ''}"


class PerPersonasGrises(models.Model):
    id_nr = models.AutoField(primary_key=True)
    id_persona = models.ForeignKey(PerPersonas, models.DO_NOTHING, db_column='id_persona')
    accion = models.CharField(max_length=10)
    id_usuario = models.ForeignKey('Usuarios', models.DO_NOTHING, db_column='id_usuario')
    fecha_registro = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'per_personas_grises'


class PerUsuariosPerfiles(models.Model):
    id_persona = models.IntegerField(primary_key=True)
    clave = models.CharField(max_length=100)
    id_perfil = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'per_usuarios_perfiles'


class PerfilArchivosActivos(models.Model):
    id_tipo_perfil = models.IntegerField(db_column='ID_TIPO_PERFIL', primary_key=True)  # Field name made lowercase. The composite primary key (ID_TIPO_PERFIL, ID_MENU) found, that is not supported. The first column is selected.
    id_menu = models.IntegerField(db_column='ID_MENU')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'perfil_archivos_activos'
        unique_together = (('id_tipo_perfil', 'id_menu'),)



class PerfilModulos(models.Model):
    id_tipo_perfil = models.OneToOneField('TipoPerfiles', models.DO_NOTHING, db_column='ID_TIPO_PERFIL', primary_key=True)  # Field name made lowercase. The composite primary key (ID_TIPO_PERFIL, ID_MODULOS) found, that is not supported. The first column is selected.
    id_modulos = models.ForeignKey(utilidades.Modulos, models.DO_NOTHING, db_column='ID_MODULOS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'perfil_modulos'
        unique_together = (('id_tipo_perfil', 'id_modulos'),)


class TipoPerfiles(models.Model):
    id_tipo_perfil = models.AutoField(db_column='ID_TIPO_PERFIL', primary_key=True)  # Field name made lowercase.
    nombre_perfil = models.CharField(db_column='NOMBRE_PERFIL', max_length=60)  # Field name made lowercase.
    id_direccion = models.IntegerField(db_column='ID_DIRECCION')  # Field name made lowercase.
    activo = models.CharField(db_column='ACTIVO', max_length=2)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tipo_perfiles'


class TipoPerfilesMenu(models.Model):
    id_tipo_perfil = models.IntegerField(db_column='ID_TIPO_PERFIL', blank=True, null=True)  # Field name made lowercase.
    id_menu = models.IntegerField(db_column='ID_MENU', blank=True, null=True)  # Field name made lowercase.
    activo = models.CharField(db_column='ACTIVO', max_length=2, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tipo_perfiles_menu'


class Usuarios(models.Model):
    id_persona = models.IntegerField(db_column='ID_PERSONA', primary_key=True)  # Field name made lowercase.
    id_tipo_perfil = models.ForeignKey(TipoPerfiles, models.DO_NOTHING, db_column='ID_TIPO_PERFIL', blank=True, null=True)  # Field name made lowercase.
    clave = models.CharField(db_column='CLAVE', max_length=120, db_collation='latin1_swedish_ci')  # Field name made lowercase.
    activo = models.CharField(db_column='ACTIVO', max_length=2, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'usuarios'

class EveTiposPersonas(models.Model):
    id_tipo_persona = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    activo = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'eve_tipos_personas'


