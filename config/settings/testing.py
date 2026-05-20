"""
Settings pour les tests automatiques (pytest).

Optimisé pour la vitesse :
- Hash de mot de passe rapide (MD5)
- Channels en mémoire (pas Redis)
- Celery en mode synchrone (eager)
- Email en mémoire
"""

from .base import *  # noqa: F401, F403
from .base import DATABASES

DEBUG = False

# Base de données de test
DATABASES["default"]["NAME"] = "sira_test"

# Hash rapide pour les tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Channels en mémoire (pas besoin de Redis pour les tests)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# Celery en mode synchrone
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Email en mémoire
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"