from django.db import models


# Create your models here.
class Info(models.Model):
    name = models.CharField(max_length=50, default="")
    team = models.CharField(max_length=50, default="")
    events = models.JSONField(default=dict)
    meets = models.JSONField(default=dict)
    pbs = models.JSONField(default=dict)
    best_performances = models.JSONField(default=dict)
    goals = models.JSONField(default=dict)

    def __str__(self):
        return self.name
