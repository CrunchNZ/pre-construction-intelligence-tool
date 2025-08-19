from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
import hashlib
import json
import time

from .models import MLModel, ModelTrainingHistory, FeatureEngineering, ModelPrediction
from .serializers import (
    MLModelSerializer, MLModelCreateSerializer, MLModelUpdateSerializer,
    ModelTrainingHistorySerializer, ModelTrainingHistoryCreateSerializer,
    FeatureEngineeringSerializer, FeatureEngineeringCreateSerializer,
    ModelPredictionSerializer, ModelPredictionCreateSerializer,
    ModelPerformanceSerializer, TrainingMetricsSerializer,
    PredictionRequestSerializer, PredictionResponseSerializer
)
from .frontend_integration import MLFrontendIntegrationService


class MLModelViewSet(viewsets.ModelViewSet):
    """ViewSet for ML Model management"""
    
    queryset = MLModel.objects.all()
    serializer_class = MLModelSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['model_type', 'status', 'algorithm', 'created_by']
    search_fields = ['name', 'description', 'algorithm']
    ordering_fields = ['created_at', 'updated_at', 'accuracy', 'last_trained']
    ordering = ['-created_at']
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.frontend_service = MLFrontendIntegrationService()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MLModelCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return MLModelUpdateSerializer
        return MLModelSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def dashboard_insights(self, request):
        """Get ML insights for dashboard"""
        try:
            insights = self.frontend_service.get_dashboard_ml_insights()
            return Response(insights, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Failed to get dashboard insights: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def project_insights(self, request):
        """Get ML insights for a specific project"""
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response(
                {'error': 'project_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            insights = self.frontend_service.get_project_ml_insights(int(project_id))
            return Response(insights, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Failed to get project insights: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def risk_analysis_insights(self, request):
        """Get ML insights for risk analysis"""
        try:
            insights = self.frontend_service.get_risk_analysis_ml_insights()
            return Response(insights, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Failed to get risk analysis insights: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def reports_insights(self, request):
        """Get ML insights for reports"""
        report_type = request.query_params.get('report_type', 'comprehensive')
        
        try:
            insights = self.frontend_service.get_reports_ml_insights(report_type)
            return Response(insights, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Failed to get reports insights: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def train(self, request, pk=None):
        """Initiate model training"""
        model = self.get_object()
        
        if model.status == 'training':
            return Response(
                {'error': 'Model is already training'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update model status
        model.status = 'training'
        model.save()
        
        # TODO: Trigger actual training process via Celery
        # This would typically involve:
        # 1. Data preparation
        # 2. Feature engineering
        # 3. Model training
        # 4. Validation
        # 5. Model saving
        
        return Response(
            {'message': f'Training started for model {model.name}'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def deploy(self, request, pk=None):
        """Deploy model to production"""
        model = self.get_object()
        
        if model.status != 'active':
            return Response(
                {'error': 'Only active models can be deployed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # TODO: Implement deployment logic
        # This would typically involve:
        # 1. Model validation
        # 2. Performance testing
        # 3. Deployment to production environment
        # 4. Health checks
        
        return Response(
            {'message': f'Model {model.name} deployed successfully'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def performance_summary(self, request):
        """Get performance summary for all models"""
        models = MLModel.objects.filter(status='active')
        
        performance_data = []
        for model in models:
            predictions_count = model.predictions.count()
            recent_predictions = model.predictions.filter(
                created_at__gte=timezone.now() - timedelta(days=30)
            )
            
            recent_accuracy = None
            if recent_predictions.exists():
                accurate_predictions = recent_predictions.filter(
                    actual_value__isnull=False
                ).exclude(actual_value=0)
                if accurate_predictions.exists():
                    recent_accuracy = sum(
                        1 for p in accurate_predictions if p.is_accurate
                    ) / accurate_predictions.count()
            
            performance_data.append({
                'model_id': model.id,
                'model_name': model.name,
                'model_type': model.model_type,
                'accuracy': model.accuracy,
                'precision': model.precision,
                'recall': model.recall,
                'f1_score': model.f1_score,
                'mae': model.mae,
                'rmse': model.rmse,
                'last_trained': model.last_trained,
                'total_predictions': predictions_count,
                'recent_accuracy': recent_accuracy
            })
        
        serializer = ModelPerformanceSerializer(performance_data, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def training_history(self, request, pk=None):
        """Get training history for a specific model"""
        model = self.get_object()
        history = model.training_history.all()
        serializer = ModelTrainingHistorySerializer(history, many=True)
        return Response(serializer.data)


class ModelTrainingHistoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Model Training History"""
    
    queryset = ModelTrainingHistory.objects.all()
    serializer_class = ModelTrainingHistorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['model', 'status', 'started_at']
    ordering_fields = ['started_at', 'training_accuracy', 'validation_accuracy']
    ordering = ['-started_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ModelTrainingHistoryCreateSerializer
        return ModelTrainingHistorySerializer
    
    @action(detail=False, methods=['get'])
    def metrics_over_time(self, request):
        """Get training metrics over time for analysis"""
        model_id = request.query_params.get('model_id')
        days = int(request.query_params.get('days', 30))
        
        queryset = self.queryset
        if model_id:
            queryset = queryset.filter(model_id=model_id)
        
        # Filter by date range
        start_date = timezone.now() - timedelta(days=days)
        queryset = queryset.filter(started_at__gte=start_date)
        
        # Get metrics over time
        metrics = []
        for history in queryset:
            metrics.append({
                'training_run_id': history.training_run_id,
                'started_at': history.started_at,
                'completed_at': history.completed_at,
                'training_accuracy': history.training_accuracy,
                'validation_accuracy': history.validation_accuracy,
                'training_loss': history.training_loss,
                'validation_loss': history.validation_loss,
                'duration_minutes': history.training_time_minutes,
                'status': history.status
            })
        
        serializer = TrainingMetricsSerializer(metrics, many=True)
        return Response(serializer.data)


class FeatureEngineeringViewSet(viewsets.ModelViewSet):
    """ViewSet for Feature Engineering"""
    
    queryset = FeatureEngineering.objects.filter(is_active=True)
    serializer_class = FeatureEngineeringSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['scaling_method', 'encoding_method', 'created_by']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return FeatureEngineeringCreateSerializer
        return FeatureEngineeringSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def validate_features(self, request, pk=None):
        """Validate feature engineering configuration"""
        feature_eng = self.get_object()
        
        # TODO: Implement feature validation logic
        # This would typically involve:
        # 1. Schema validation
        # 2. Data type checking
        # 3. Range validation
        # 4. Consistency checks
        
        validation_result = {
            'is_valid': True,
            'warnings': [],
            'errors': []
        }
        
        return Response(validation_result)


class ModelPredictionViewSet(viewsets.ModelViewSet):
    """ViewSet for Model Predictions"""
    
    queryset = ModelPrediction.objects.all()
    serializer_class = ModelPredictionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['model', 'project_id', 'user_id', 'created_at']
    ordering_fields = ['created_at', 'prediction_value', 'prediction_confidence']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ModelPredictionCreateSerializer
        return ModelPredictionSerializer
    
    @action(detail=False, methods=['post'])
    def predict(self, request):
        """Make a prediction using a trained model"""
        serializer = PredictionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        model_id = data['model_id']
        input_features = data['input_features']
        
        try:
            model = MLModel.objects.get(id=model_id, status='active')
        except MLModel.DoesNotExist:
            return Response(
                {'error': 'Model not found or not active'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        start_time = time.time()
        
        # Generate input data hash for deduplication
        input_hash = hashlib.sha256(
            json.dumps(input_features, sort_keys=True).encode()
        ).hexdigest()
        
        # TODO: Implement actual prediction logic
        # This would typically involve:
        # 1. Feature preprocessing
        # 2. Model loading
        # 3. Prediction generation
        # 4. Confidence calculation
        # 5. Interval estimation
        
        # Placeholder prediction (replace with actual ML model)
        prediction_value = 1000.0  # Placeholder
        prediction_confidence = 0.85  # Placeholder
        prediction_interval_lower = 900.0  # Placeholder
        prediction_interval_upper = 1100.0  # Placeholder
        
        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Store prediction
        prediction = ModelPrediction.objects.create(
            model=model,
            input_features=input_features,
            input_data_hash=input_hash,
            prediction_value=prediction_value,
            prediction_confidence=prediction_confidence,
            prediction_interval_lower=prediction_interval_lower,
            prediction_interval_upper=prediction_interval_upper,
            project_id=data.get('project_id', ''),
            user_id=data.get('user_id', '')
        )
        
        response_data = {
            'prediction_id': prediction.id,
            'prediction_value': prediction_value,
            'prediction_confidence': prediction_confidence,
            'prediction_interval_lower': prediction_interval_lower,
            'prediction_interval_upper': prediction_interval_upper,
            'model_name': model.name,
            'model_version': model.version,
            'created_at': prediction.created_at,
            'processing_time_ms': processing_time
        }
        
        serializer = PredictionResponseSerializer(response_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def accuracy_analysis(self, request):
        """Analyze prediction accuracy over time"""
        model_id = request.query_params.get('model_id')
        days = int(request.query_params.get('days', 30))
        
        queryset = self.queryset.filter(actual_value__isnull=False)
        if model_id:
            queryset = queryset.filter(model_id=model_id)
        
        # Filter by date range
        start_date = timezone.now() - timedelta(days=days)
        queryset = queryset.filter(created_at__gte=start_date)
        
        # Calculate accuracy metrics
        total_predictions = queryset.count()
        accurate_predictions = sum(1 for p in queryset if p.is_accurate)
        overall_accuracy = accurate_predictions / total_predictions if total_predictions > 0 else 0
        
        # Calculate error statistics
        errors = [p.prediction_error for p in queryset if p.prediction_error is not None]
        mean_error = sum(errors) / len(errors) if errors else 0
        mean_absolute_error = sum(abs(e) for e in errors) / len(errors) if errors else 0
        
        analysis = {
            'total_predictions': total_predictions,
            'accurate_predictions': accurate_predictions,
            'overall_accuracy': overall_accuracy,
            'mean_error': mean_error,
            'mean_absolute_error': mean_absolute_error,
            'error_distribution': {
                'positive_errors': len([e for e in errors if e > 0]),
                'negative_errors': len([e for e in errors if e < 0]),
                'zero_errors': len([e for e in errors if e == 0])
            }
        }
        
        return Response(analysis)
