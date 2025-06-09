import re
from django.core.exceptions import ValidationError

def validar_rut(value):
    # Validar formato básico
    rut_regex = re.compile(r'^0*(\d{1,3}(\.?\d{3})*)-([\dkK])$')
    if not rut_regex.match(value):
        raise ValidationError("RUT INVALIDO")

    # Extraer número base y dígito verificador
    rut = value.replace('.', '').replace('-', '').upper()
    numero = int(rut[:-1])
    dv = rut[-1]

    # Calcular el dígito verificador esperado
    suma = 0
    multiplo = 2
    for digito in reversed(str(numero)):
        suma += int(digito) * multiplo
        multiplo = multiplo + 1 if multiplo < 7 else 2

    resto = suma % 11
    dv_esperado = str(11 - resto) if resto != 0 else '0'
    if resto == 1:
        dv_esperado = 'K'

    # Comparar dígito verificador
    if dv != dv_esperado:
        raise ValidationError('Dígito verificador incorrecto.')