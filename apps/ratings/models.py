"""
Modèles d'évaluation Sira.
- Rating : évaluation bidirectionnelle client ↔ conducteur après chaque course.
  Max 2 ratings par course (client→driver ET driver→client).
  Contrainte unique : (ride, rater) — on ne peut noter qu'une fois par course.
"""
from django.conf import settings
from django.db import models

from apps.core.models import TimestampedModel
from apps.rides.models import Ride


class Rating(TimestampedModel):

    ride    = models.ForeignKey(
                  Ride,
                  on_delete=models.CASCADE,
                  related_name="ratings",
              )
    rater   = models.ForeignKey(
                  settings.AUTH_USER_MODEL,
                  on_delete=models.CASCADE,
                  related_name="ratings_given",
              )
    rated   = models.ForeignKey(
                  settings.AUTH_USER_MODEL,
                  on_delete=models.CASCADE,
                  related_name="ratings_received",
              )
    score   = models.PositiveSmallIntegerField(
                  choices=[(i, str(i)) for i in range(1, 6)]
              )
    comment   = models.TextField(max_length=500, blank=True)
    is_flagged = models.BooleanField(default=False)
    is_hidden  = models.BooleanField(default=False)

    class Meta:
        db_table        = "sira_rating"
        verbose_name    = "Évaluation"
        verbose_name_plural = "Évaluations"
        constraints     = [
            models.UniqueConstraint(
                fields=["ride", "rater"],
                name="unique_rating_per_ride_rater",
            ),
        ]
        indexes         = [
            models.Index(fields=["rated"]),
            models.Index(fields=["ride"]),
        ]

    def __str__(self):
        return f"Rating {self.ride_id} — {self.rater} → {self.rated} ({self.score}/5)"