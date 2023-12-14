from django.contrib.auth.models import User
from django.utils.timezone import now
from django.conf import settings
from django.db import models
    
    
class ForecastModel(models.Model):
    """This model will store the results of the sales forecasting for each industry."""
    INDUSTRY_CHOICES = [(i['Industry'], i['Industry']) for i in settings.INDUSTRIES]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES)
    forecasted_data = models.JSONField()  # Store forecasted sales data in JSON format
    date = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.industry} - Sales Forecasting Result"
