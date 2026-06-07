from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('recommendation/', views.recommendation_view, name='recommendation'),
]
