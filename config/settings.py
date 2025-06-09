import os
from pathlib import Path
from dotenv import load_dotenv

# ─── Paths ─────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

import pymysql
pymysql.install_as_MySQLdb()

# ─── Seguridad y entorno ───────────────
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "insecure-default")
DEBUG = os.getenv("DJANGO_DEBUG", "False") == "True"


def _split_env_list(var_name: str) -> list[str]:
    """Split an environment variable into a list, dropping empty values."""
    return [v for v in os.getenv(var_name, "").split(",") if v]

ALLOWED_HOSTS = (
    ["127.0.0.1", "localhost"] if DEBUG else _split_env_list("DJANGO_ALLOWED_HOSTS")
)

# ─── CORS y CSRF ───────────────────────
CORS_ALLOWED_ORIGINS = _split_env_list("CORS_ALLOWED_ORIGINS") if not DEBUG else []
CSRF_TRUSTED_ORIGINS = _split_env_list("CSRF_TRUSTED_ORIGINS") if not DEBUG else []


# ─── Seguridad en producción ───────────
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

LOGIN_URL = "/usuarios/login/"
LOGIN_REDIRECT_URL = "/usuarios/home/"

# ─── Apps ──────────────────────────────
INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3rd party (agrega aquí lo que uses realmente)
    "rest_framework",
    "corsheaders",
    "storages",     # S3, si usas S3 para media
    "axes",
    "widget_tweaks",
    # Apps propias
    "apps.eventos",
    "apps.mapas",
    "apps.usuarios",
    "apps.empresas",
    "apps.mantenedores",
    "apps.personas",
    "apps.dispositivos",
    "apps.utilidades",
    "apps.vehiculos"    
]

# ─── Middleware ────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
    "config.middlewares.LoginRequiredMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# ─── Templates ─────────────────────────
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],  # Globales
    "APP_DIRS": True,
    "OPTIONS": {
        "context_processors": [
            "django.template.context_processors.debug",
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ],
    },
}]

# ─── Base de datos (MySQL ejemplo) ─────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE'",
            "charset": "utf8mb4",
            "use_unicode": True,
        },
    }
}
# Cambia ENGINE y opciones si luego usas PostgreSQL:
# "ENGINE": "django.db.backends.postgresql"

# ─── Validación de contraseñas ─────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ─── Internacionalización ──────────────
LANGUAGE_CODE = "es"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = False

# ─── Static & Media ────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ─── Media (opcional S3) ───────────────
# Si usas S3 para media (puedes comentar si no usas)
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "us-east-1")
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com" if AWS_STORAGE_BUCKET_NAME else ""
MEDIA_LOCATION = "media"
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIA_LOCATION}/" if AWS_S3_CUSTOM_DOMAIN else "/media/"

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage" if AWS_STORAGE_BUCKET_NAME else "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "region_name": AWS_S3_REGION_NAME,
            "custom_domain": AWS_S3_CUSTOM_DOMAIN,
            "location": MEDIA_LOCATION,
        } if AWS_STORAGE_BUCKET_NAME else {},
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ─── Campo auto por defecto ────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ─── Otros (logging, etc.) ─────────────
# Deja el logging simple; agrega solo si lo necesitas en desarrollo.
