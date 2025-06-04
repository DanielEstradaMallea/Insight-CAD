from django.conf import settings
from django.shortcuts import redirect

EXEMPT_URLS = [
    settings.LOGIN_URL,
    '/usuarios/registrar/',
    '/usuarios/logout/',
    '/admin/login/',
]

if hasattr(settings, 'STATIC_URL'):
    EXEMPT_URLS.append(settings.STATIC_URL)
if hasattr(settings, 'MEDIA_URL'):
    EXEMPT_URLS.append(settings.MEDIA_URL)

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info

        # Si la URL comienza con alguna exenta, no pide login
        if not request.user.is_authenticated:
            if not any(path == url or path.startswith(url) for url in EXEMPT_URLS):
                return redirect(settings.LOGIN_URL)
        return self.get_response(request)
