from django.db import models


class LastService(models.Model):
    date_time = models.DateTimeField(auto_now=False)

    def __str__(self, *args, **kwargs):
        return str(self.date_time)


class LastRepair(models.Model):
    date_time = models.DateTimeField(auto_now=False)

    def __str__(self, *args, **kwargs):
        return str(self.date_time)
