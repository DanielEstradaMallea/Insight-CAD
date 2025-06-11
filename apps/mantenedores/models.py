from django.db import models

class AdmComunas(models.Model):
    id_comuna = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=120)
    activo = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'adm_comunas'


class AdmEstadosCiviles(models.Model):
    id_estado_civil = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=60)
    activo = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'adm_estados_civiles'


class AdmGenero(models.Model):
    id_genero = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=60)
    activo = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'adm_genero'


class AdmPaises(models.Model):
    id_pais = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=80)
    iso = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'adm_paises'
