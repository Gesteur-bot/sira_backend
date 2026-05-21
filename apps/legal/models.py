"""
Modèles légaux Sira.
- LegalDocument  : documents légaux versionnés (CGU, confidentialité)
- UserAcceptance : traçabilité des acceptations (pièce maîtresse juridique)
"""
from django.conf import settings
from django.db import models

from apps.core.models import TimestampedModel


class LegalDocument(TimestampedModel):

    class DocumentType(models.TextChoices):
        TERMS_PLATFORM = "TERMS_PLATFORM", "CGU Plateforme"
        TERMS_DRIVER   = "TERMS_DRIVER",   "CGU Conducteur"
        TERMS_CLIENT   = "TERMS_CLIENT",   "CGU Client"
        PRIVACY_POLICY = "PRIVACY_POLICY", "Politique de confidentialité"

    document_type  = models.CharField(max_length=20, choices=DocumentType.choices)
    version        = models.CharField(max_length=20)  # ex : '1.0', '2.1'
    title          = models.CharField(max_length=200)
    content        = models.TextField()  # Markdown ou HTML
    is_active      = models.BooleanField(default=False)
    effective_from = models.DateTimeField()
    created_by     = models.ForeignKey(
                         settings.AUTH_USER_MODEL,
                         on_delete=models.PROTECT,
                         related_name="created_legal_documents",
                     )

    class Meta:
        db_table        = "sira_legal_document"
        verbose_name    = "Document légal"
        verbose_name_plural = "Documents légaux"
        # Une seule version active par type de document
        constraints = [
            models.UniqueConstraint(
                fields=["document_type"],
                condition=models.Q(is_active=True),
                name="unique_active_document_per_type",
            ),
            models.UniqueConstraint(
                fields=["document_type", "version"],
                name="unique_version_per_document_type",
            ),
        ]

    def __str__(self):
        return f"{self.document_type} v{self.version} ({'active' if self.is_active else 'inactive'})"


class UserAcceptance(TimestampedModel):
    """
    Trace d'acceptation d'un document légal.
    PIÈCE MAÎTRESSE en cas de litige juridique.
    Contrainte unique : un user ne peut pas accepter deux fois la même version.
    """

    class AcceptanceMethod(models.TextChoices):
        CHECKBOX        = "CHECKBOX",        "Case à cocher"
        CHECKBOX_TYPED  = "CHECKBOX_TYPED",  "Case + phrase saisie"
        SIGNATURE       = "SIGNATURE",       "Signature"

    user              = models.ForeignKey(
                            settings.AUTH_USER_MODEL,
                            on_delete=models.PROTECT,
                            related_name="legal_acceptances",
                        )
    document          = models.ForeignKey(
                            LegalDocument,
                            on_delete=models.PROTECT,
                            related_name="acceptances",
                        )
    accepted_at       = models.DateTimeField(auto_now_add=True)
    ip_address        = models.GenericIPAddressField()
    user_agent        = models.TextField()
    acceptance_method = models.CharField(
                            max_length=20,
                            choices=AcceptanceMethod.choices,
                            default=AcceptanceMethod.CHECKBOX,
                        )
    typed_confirmation = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table        = "sira_user_acceptance"
        verbose_name    = "Acceptation CGU"
        verbose_name_plural = "Acceptations CGU"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "document"],
                name="unique_acceptance_per_user_document",
            ),
        ]

    def __str__(self):
        return f"{self.user} — {self.document} ({self.accepted_at.date()})"