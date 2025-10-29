from django.db import models

class ItemsHistory(models.Model):
    config_id = models.AutoField(primary_key=True)
    api_params = models.JSONField()
    last_id = models.PositiveBigIntegerField(default=0)

class APIParameter(models.Model):
    id = models.AutoField(primary_key=True)
    section = models.CharField(max_length=200, null=False)
    sub_section = models.CharField(max_length=200, null=True)
    name = models.CharField(max_length=200, null=False)
    value = models.PositiveIntegerField(null=False)