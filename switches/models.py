from __future__ import unicode_literals

from django.db import models

from blinkers.models import NewHope

# Create your models here.
class FarFarAway(models.Model):
  hope = models.ForeignKey(NewHope)
  last = models.IntegerField(default=12)
