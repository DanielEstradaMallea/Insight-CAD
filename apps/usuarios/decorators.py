# apps/usuarios/decorators.py
from django.contrib.auth.decorators import user_passes_test

def groups_required(group_names, login_url='usuarios:login'):
    """
    Permite el acceso si el usuario pertenece a cualquiera de los grupos indicados.
    `group_names` puede ser:
      - Una lista de strings:   ['Administrador','Editor', 'Visualizador', 'Ingresador']
      - Una cadena separada:    "admin, editores"
    """
    def in_any_group(user):
        if not getattr(user, 'is_authenticated', False):
            return False
        # normalizamos a lista de nombres
        if isinstance(group_names, str):
            names = [g.strip() for g in group_names.split(',')]
        else:
            names = list(group_names)
        # True si al menos uno coincide
        return user.groups.filter(name__in=names).exists()

    return user_passes_test(in_any_group, login_url=login_url)