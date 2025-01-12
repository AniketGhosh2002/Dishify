from django.db import models


class RecipeRequest(models.Model):
    ingredients = models.TextField()
    cuisine = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

