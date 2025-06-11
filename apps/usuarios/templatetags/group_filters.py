from django import template

register = template.Library()

@register.filter
def in_group(user, group_name):
    if not hasattr(user, 'groups'):
        return False
    return user.is_authenticated and user.groups.filter(name=group_name).exists()

@register.filter
def in_groups(user, group_names):
    """
    Recibe una cadena con nombres de grupo separados por comas,
    y devuelve True si el usuario pertenece a cualquiera de ellos.
    """
    if not user.is_authenticated or not hasattr(user, 'groups'):
        return False
    # Dividimos y limpiamos espacios
    names = [g.strip() for g in group_names.split(',')]
    # Comprueba si existe al menos uno
    return user.groups.filter(name__in=names).exists()