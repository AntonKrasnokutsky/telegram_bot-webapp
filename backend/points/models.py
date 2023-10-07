from django.db import models


class Points(models.Model):
    name = models.TextField()

    def __str__(self, *args, **kwargs):
        return str(self.name)
