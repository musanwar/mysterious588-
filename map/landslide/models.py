from django.db import models

class Cracks(models.Model):
    long = models.TextField()
    lat = models.TextField()
    date = models.DateTimeField(auto_now=True)
