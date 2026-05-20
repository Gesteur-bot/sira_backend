"""
URLs principales du projet Sira.

Les URLs métier seront ajoutées progressivement au fur et à mesure
de la création des apps (accounts, drivers, rides, etc.).
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Admin Django
    path("admin/", admin.site.urls),

    # Documentation API (auto-générée)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),

    # API v1 — à brancher progressivement
    # path("api/v1/auth/", include("apps.accounts.urls")),
    # path("api/v1/drivers/", include("apps.drivers.urls")),
    # path("api/v1/rides/", include("apps.rides.urls")),
    # path("api/v1/payments/", include("apps.payments.urls")),
]

# Servir les fichiers média en dev uniquement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Debug toolbar
    try:
        import debug_toolbar

        urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
    except ImportError:
        pass