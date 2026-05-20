"""
Settings de développement local.

Surcharges par rapport à base.py :
- DEBUG=True pour avoir les pages d'erreur détaillées
- ALLOWED_HOSTS permissif
- CORS permissif (toutes origines pour faciliter tests app mobile)
- Logs en console plus verbeux
- Pas d'HTTPS forcé
"""

from .base import * # noqa: F401, F403
from .base import INSTALLED_APPS, MIDDLEWARE

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Ajout des outils de dev
INSTALLED_APPS += [
    "debug_toolbar",
    "django_extensions",
]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

INTERNAL_IPS = ["127.0.0.1", "localhost"]

# Email en console (au lieu d'envoyer vraiment)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# CORS permissif en dev pour tester l'app mobile facilement
CORS_ALLOW_ALL_ORIGINS = True

# Logging plus verbeux
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django.db.backends": {
            "handlers": ["console"],
            "level": "WARNING",  # WARNING pour éviter le spam SQL
        },
        "sira": {
            "handlers": ["console"],
            "level": "DEBUG",  # DEBUG pour notre code à nous
            "propagate": False,
        },
    },
}