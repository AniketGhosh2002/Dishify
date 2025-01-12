from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('generate-recipe/', views.generate_recipe, name='generate_recipe'),
]
