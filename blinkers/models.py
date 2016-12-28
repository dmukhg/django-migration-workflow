from django.db import models

# Create your models here.
class NewHope(models.Model):
  xml = models.TextField()
  title = models.CharField(max_length=100)
  fetch = models.IntegerField(default=12)
