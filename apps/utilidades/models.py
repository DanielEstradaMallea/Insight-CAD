from django.db import models

from django.db import models
from apps.mantenedores import models as mantenedor
from apps.dispositivos import models as dispositivo
from apps.empresas import models as empresa
from apps.eventos import models as evento




class AdmPerfiles(models.Model):
    id_perfil = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=60)
    activo = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'adm_perfiles'


class Archivos(models.Model):
    id_archivo = models.AutoField(db_column='ID_ARCHIVO', primary_key=True)  # Field name made lowercase.
    nombre_archivo = models.CharField(db_column='NOMBRE_ARCHIVO', max_length=60)  # Field name made lowercase.
    nombre_muestra = models.TextField(db_column='NOMBRE_MUESTRA')  # Field name made lowercase.
    ruta = models.CharField(db_column='RUTA', max_length=30, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'archivos'



class EveIaMail(models.Model):
    id_ia_mail = models.AutoField(primary_key=True)
    id_evento = models.IntegerField(blank=True, null=True)
    mail = models.CharField(max_length=120, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'eve_ia_mail'


class EveIaResumen(models.Model):
    id_ia_resumen = models.AutoField(primary_key=True)
    id_evento = models.IntegerField(blank=True, null=True)
    resumen = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'eve_ia_resumen'


class EveIaTelefono(models.Model):
    id_ia_telefono = models.AutoField(primary_key=True)
    id_evento = models.IntegerField(blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'eve_ia_telefono'


class EveMatchPersonas(models.Model):
    id_persona = models.IntegerField(primary_key=True)  # The composite primary key (id_persona, id_evento) found, that is not supported. The first column is selected.
    id_evento = models.IntegerField()
    alerta_encendida = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'eve_match_personas'
        unique_together = (('id_persona', 'id_evento'),)


class EveMatchVehiculos(models.Model):
    id_vehiculo = models.IntegerField(primary_key=True)  # The composite primary key (id_vehiculo, id_evento) found, that is not supported. The first column is selected.
    id_evento = models.IntegerField()
    alerta_encendida = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'eve_match_vehiculos'
        unique_together = (('id_vehiculo', 'id_evento'),)


class EvePersonasEventos(models.Model):
    id_persona = models.IntegerField()
    id_evento = models.IntegerField()
    id_tipo_persona = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'eve_personas_eventos'
        unique_together = (('id_persona', 'id_evento'),)
        
class EvePersonasEventosPK(models.Model):
    id = models.AutoField(primary_key=True)
    id_persona = models.IntegerField()
    id_evento = models.IntegerField()
    id_tipo_persona = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'eve_personas_eventos'
        unique_together = (('id_persona', 'id_evento'),)



class EveVehiculosEventos(models.Model):
    id_vehiculo = models.IntegerField()  
    id_evento = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'eve_vehiculos_eventos'
        unique_together = (('id_vehiculo', 'id_evento'),)


class Menu(models.Model):
    id_menu = models.AutoField(db_column='ID_MENU', primary_key=True)  # Field name made lowercase.
    nombre_menu = models.CharField(db_column='NOMBRE_MENU', max_length=60, blank=True, null=True)  # Field name made lowercase.
    id_menu_padre = models.IntegerField(db_column='ID_MENU_PADRE', blank=True, null=True)  # Field name made lowercase.
    codigo_menu = models.CharField(db_column='CODIGO_MENU', max_length=4, blank=True, null=True)  # Field name made lowercase.
    activo = models.CharField(db_column='ACTIVO', max_length=2, blank=True, null=True)  # Field name made lowercase.
    id_archivo = models.IntegerField(db_column='ID_ARCHIVO', blank=True, null=True)  # Field name made lowercase.
    icono = models.CharField(db_column='ICONO', max_length=30, blank=True, null=True)  # Field name made lowercase.
    tiene_hijo = models.CharField(db_column='TIENE_HIJO', max_length=2, blank=True, null=True)  # Field name made lowercase.
    nivel = models.CharField(db_column='NIVEL', max_length=10, blank=True, null=True)  # Field name made lowercase.
    link_especial = models.CharField(db_column='LINK_ESPECIAL', max_length=60, blank=True, null=True)  # Field name made lowercase.
    orden = models.IntegerField(db_column='ORDEN', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'menu'


class Modulos(models.Model):
    id_modulos = models.AutoField(db_column='ID_MODULOS', primary_key=True)  # Field name made lowercase.
    nombre_modulos = models.CharField(db_column='NOMBRE_MODULOS', max_length=30)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'modulos'


class ModulosArchivos(models.Model):
    id_archivo = models.OneToOneField(Archivos, models.DO_NOTHING, db_column='ID_ARCHIVO', primary_key=True)  # Field name made lowercase. The composite primary key (ID_ARCHIVO, ID_MODULOS) found, that is not supported. The first column is selected.
    id_modulos = models.ForeignKey(Modulos, models.DO_NOTHING, db_column='ID_MODULOS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'modulos_archivos'
        unique_together = (('id_archivo', 'id_modulos'),)


class ModulosMenu(models.Model):
    id_modulos = models.OneToOneField(Modulos, models.DO_NOTHING, db_column='ID_MODULOS', primary_key=True)  # Field name made lowercase. The composite primary key (ID_MODULOS, ID_MENU) found, that is not supported. The first column is selected.
    id_menu = models.ForeignKey(Menu, models.DO_NOTHING, db_column='ID_MENU')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'modulos_menu'
        unique_together = (('id_modulos', 'id_menu'),)





