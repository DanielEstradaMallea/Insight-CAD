from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()  # Obtiene el usuario validado
            login(request, user)    # Autentica al usuario
            return redirect('home')  # Redirige a una vista principal

    else:
        form = AuthenticationForm()

    return render(request, 'usuarios/login.html', {'form': form})

def home_view(request):
    usuario = request.user
    grupos = usuario.groups.all()
    return render(request, 'mapas/mapa.html', {
        'usuario': usuario,
        'grupos': grupos
    })
