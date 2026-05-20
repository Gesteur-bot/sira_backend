"""
Configuration Django commune à tous les environnements.

Ce fichier contient :
- La configuration générale Django (apps, middleware, etc.)
- La configuration de la base de données PostgreSQL + PostGIS
- La configuration sécurité (JWT, CORS, HTTPS-ready)
- La configuration WebSocket (Channels + Redis)
- La configuration tâches asynchrones (Celery)
- Toutes les constantes métier Sira (matching, anti-fraude, etc.)

Décisions de cadrage intégrées :
- User personnalisé (apps.accounts.User) avec rôle obligatoire
- Profils séparés par rôle (ClientProfile, DriverProfile, AdminProfile)
- Un compte = un seul rôle (strict)
- Mode offline géré côté app, backend reçoit/stocke/transmet
- Module paiement flexible (2 scénarios : direct ou wallet)
"""
import os

from datetime import timedelta
from pathlib import Path

import environ

# ---------------------------------------------------------------------------
# Chemins de base
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------------------
# Variables d'environnement (lues depuis .env)
# ---------------------------------------------------------------------------
env = environ.Env()
environ.Env.read_env(os.path.join(Path(__file__).resolve().parent.parent.parent, '.env'))

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=['localhost', '127.0.0.1', '192.168.10.131'])

GDAL_LIBRARY_PATH = env("GDAL_LIBRARY_PATH")
GEOS_LIBRARY_PATH = env("GEOS_LIBRARY_PATH")

# ---------------------------------------------------------------------------
# Applications installées
# ---------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",  # CRITIQUE : pour PostGIS et les PointField
]

THIRD_PARTY_APPS = [
    "rest_framework",                       # API REST
    "rest_framework_simplejwt",             # JWT
    "rest_framework_simplejwt.token_blacklist",  # Blacklist refresh tokens
    "corsheaders",                          # CORS pour app mobile
    "django_filters",                       # Filtrage DRF
    "drf_spectacular",                      # Doc OpenAPI/Swagger
    "channels",                             # WebSocket
    "phonenumber_field",                    # Numéros internationaux
    "storages",                             # Stockage objet S3
    "django_celery_beat",                   # Tâches planifiées Celery
]

# Apps Sira (à activer au fur et à mesure de leur création)
LOCAL_APPS = [
     "apps.core",
     "apps.accounts",
    # "apps.legal",
     "apps.drivers",
    # "apps.rides",
    # "apps.payments",
    # "apps.ratings",
    # "apps.pricing",
    # "apps.matching",
    # "apps.disputes",
    # "apps.sanctions",
    # "apps.safety",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ---------------------------------------------------------------------------
# Middleware (ordre important !)
# ---------------------------------------------------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # Doit être en premier
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"  # Pour Channels (WebSocket)

# ---------------------------------------------------------------------------
# Base de données — PostgreSQL + PostGIS
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST", default="localhost"),
        "PORT": env("POSTGRES_PORT", default="5432"),
        "CONN_MAX_AGE": 60,
        "OPTIONS": {
            "connect_timeout": 10,
        },
    }
}

# ---------------------------------------------------------------------------
# Authentification — User Sira (sera créé dans l'app accounts)
# ---------------------------------------------------------------------------
# Ce paramètre sera activé quand on créera l'app accounts
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Internationalisation — Burkina Faso
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "fr-bf"
TIME_ZONE = "Africa/Ouagadougou"
USE_I18N = True
USE_TZ = True

# Numéros de téléphone (format Burkina Faso par défaut)
PHONENUMBER_DEFAULT_REGION = "BF"

# ---------------------------------------------------------------------------
# Fichiers statiques et médias
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",      # IP non authentifiée : 100 req/h
        "user": "1000/hour",     # Utilisateur authentifié : 1000 req/h
        "login": "5/minute",     # Tentatives de login : 5/min (anti brute force)
        "otp": "3/minute",       # Demandes d'OTP : 3/min
    },
}

# ---------------------------------------------------------------------------
# JWT (sécurité authentification API)
# ---------------------------------------------------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),    # Token courte durée
    "REFRESH_TOKEN_LIFETIME": timedelta(days=14),       # Refresh long
    "ROTATE_REFRESH_TOKENS": True,                      # Sécurité : nouveau refresh à chaque usage
    "BLACKLIST_AFTER_ROTATION": True,                   # Empêche réutilisation
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "TOKEN_TYPE_CLAIM": "token_type",
}

# ---------------------------------------------------------------------------
# Channels (WebSocket)
# ---------------------------------------------------------------------------
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [env("REDIS_URL", default="redis://redis26@192.168.10.131:6379/0")],
            "capacity": 1500,    # Messages max par groupe
            "expiry": 60,        # Expiration messages en secondes
        },
    },
}

# ---------------------------------------------------------------------------
# Celery (tâches asynchrones)
# ---------------------------------------------------------------------------
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://redis26@192.168.10.131:6379/1")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://redis26@192.168.10.131:6379/2")
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 5 * 60  # 5 minutes max par tâche
CELERY_TASK_SOFT_TIME_LIMIT = 60  # Avertissement après 1 minute
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# ---------------------------------------------------------------------------
# CORS (sécurité pour app mobile et frontend admin)
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "x-idempotency-key",   # Pour les paiements
]

# ---------------------------------------------------------------------------
# Documentation API (Swagger / OpenAPI)
# ---------------------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    "TITLE": "Sira API",
    "DESCRIPTION": "API de la plateforme Sira — taxis-motos Burkina Faso",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
}

# ---------------------------------------------------------------------------
# Sécurité - Cookies et headers
# ---------------------------------------------------------------------------
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# Note : les paramètres HTTPS (SECURE_SSL_REDIRECT, HSTS, etc.) sont activés
# uniquement en production. Voir production.py

# ===========================================================================
# CONSTANTES MÉTIER SIRA
# ===========================================================================
# Ces valeurs sont AUSSI persistées en base via les modèles MatchingConfiguration
# et PricingRule pour être ajustables par l'admin sans redéploiement.
# Les valeurs ici servent de FALLBACK initial.
# ---------------------------------------------------------------------------

# --- Anti-fraude GPS ---
SIRA_DISTANCE_FRAUD_TOLERANCE = 0.10        # 10% écart distance GPS vs théorique
SIRA_MAX_REASONABLE_SPEED_KMH = 80          # Vitesse max d'une moto
SIRA_MIN_GPS_ACCURACY_M = 50                # Précision GPS minimale acceptée
SIRA_MAX_GPS_POINT_GAP_SECONDS = 60         # Gap max entre 2 points GPS

# --- Matching (algorithme de mise en relation) ---
SIRA_INITIAL_SEARCH_RADIUS_M = 1000         # Rayon initial 1 km
SIRA_MAX_SEARCH_RADIUS_M = 5000             # Rayon max 5 km
SIRA_DISPATCH_BATCH_SIZE = 3                # Notifier 3 conducteurs en parallèle
SIRA_DRIVER_RESPONSE_TIMEOUT_S = 15         # 15s pour accepter une course
SIRA_TOTAL_DISPATCH_TIMEOUT_S = 90          # Abandon recherche après 90s

# Pondération du matching (somme = 1.0)
SIRA_MATCHING_WEIGHT_DISTANCE = 0.55
SIRA_MATCHING_WEIGHT_SCORE = 0.30
SIRA_MATCHING_WEIGHT_WAITING = 0.15

# --- Score conducteur ---
SIRA_DEFAULT_DRIVER_SCORE = 70.00           # Score initial d'un nouveau conducteur
SIRA_SCORE_SUSPENSION_THRESHOLD = 30.00     # < 30 : suspension auto du matching
SIRA_SCORE_WARNING_THRESHOLD = 50.00        # < 50 : pénalité matching

# --- OTP (vérification téléphone) ---
SIRA_OTP_VALIDITY_MINUTES = 10              # Code valide 10 minutes
SIRA_OTP_MAX_ATTEMPTS = 5                   # Max 5 tentatives erronées
SIRA_OTP_RESEND_COOLDOWN_S = 60             # 60s entre 2 envois OTP

# --- Partage position destinataire (livraisons) ---
SIRA_RECIPIENT_SHARE_TOKEN_VALIDITY_H = 2   # Lien SMS valide 2 heures

# --- Synchronisation offline ---
SIRA_OFFLINE_SYNC_MAX_DELAY_H = 24          # Au-delà : course rejetée

# --- Paiements ---
SIRA_PAYMENT_MODE = env("PAYMENT_MODE", default="DIRECT")  # DIRECT ou WALLET
SIRA_COMMISSION_PERCENT = env.float("SIRA_COMMISSION_PERCENT", default=15.0)
SIRA_PAYMENT_IDEMPOTENCY_TTL_H = 24         # TTL des clés d'idempotence

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "sira": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}