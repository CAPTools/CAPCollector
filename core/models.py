"""CAP Collector models."""

__author__ = "arcadiy@google.com (Arkadii Yakovets)"


from django.db import models
from django.utils.translation import ugettext as _


class Alert(models.Model):
  """Alert entity definition."""
  uuid = models.CharField(_("Alert UUID"), max_length=36, db_index=True)
  created_at = models.DateTimeField(_("Alert creation time"), db_index=True)
  expires_at = models.DateTimeField(_("Alert expiration time"), db_index=True)
  content = models.TextField(_("Alert content"))

  def __unicode__(self):
    return self.uuid
