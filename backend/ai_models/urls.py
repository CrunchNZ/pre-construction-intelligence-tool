"""
URL configuration for ai_models app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'models', views.MLModelViewSet, basename='mlmodel')
router.register(r'training-history', views.ModelTrainingHistoryViewSet, basename='traininghistory')
router.register(r'feature-engineering', views.FeatureEngineeringViewSet, basename='featureengineering')
router.register(r'predictions', views.ModelPredictionViewSet, basename='prediction')

app_name = 'ai_models'

urlpatterns = [
    path('', include(router.urls)),
]
